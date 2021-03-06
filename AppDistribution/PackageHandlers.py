import biplist
import os
import re
import shutil
from datetime import datetime
from zipfile import ZipFile
from tempfile import mkdtemp, mkstemp
from androguard.core import androconf
from androguard.core.bytecodes import apk
from elementtree.ElementTree import Element, parse
from xml.dom import minidom
from uuid import uuid1

from django.core.files import File

from AppDistribution.models import *
from AppDistribution import settings
from UnCrushPNG import updatePNG
from AppDistribution import S3UploadTask
from hashlib import md5


class PackageHandler(object):

    def __init__(self, asset):
        self.asset = asset
        if asset.app.device_type == "IOS":
            self.handler = iOSPackageHandler(asset)
        elif asset.app.device_type == "ANDROID":
            self.handler = AndroidPackageHandler(asset)
            

    def handle(self):
        self.handler.handle_package()
        asset_fp = open(self.asset.asset_file.path)
        file_hash = md5(asset_fp.read())

        self.asset.file_hash = file_hash.hexdigest()
        self.asset.save()
        from AppDistribution.models import SpoutSite
        site = SpoutSite.objects.get_current()
        try:
            site = SpoutSite.objects.get_current()
            if site.s3_upload_enabled:
                S3UploadTask.upload_asset_to_s3.delay(self.asset, site.aws_access_key, site.aws_secret_key, site.s3_upload_bucket)
        except:
            #TODO: Let's log someday.
            pass



    def upload_asset_to_s3(self, asset):

        connection = S3Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)

        asset_bucket = connection.get_bucket(settings.S3_ASSET_BUCKET)
        asset_path = asset.asset_file.path
        asset_file = open(asset_path)

        tag_string = "-".join([tag.name.replace("/", "-") for tag in asset.app.tags.all()])
        product = asset.app.product.name
        file_extension = os.path.splitext(asset_path)[-1]
        version = asset.app.version

        key_name = "%s-%s-%s%s" % (product, tag_string, version, file_extension)

        app_key = Key(asset_bucket, key_name)
        app_key.set_contents_from_file(open(asset_path))
        app_key.make_public()
        metadata = {'version' : version, 'product' : product}
        app_key.set_remote_metadata(metadata, {}, preserve_acl=True)
        asset.external_url = app_key.generate_url(0, query_auth=False)
        asset.save()



class AndroidPackageHandler(object):

    def __init__(self, asset):


        self.app = asset.app
        temp_file, temp_file_path = mkstemp()
        shutil.copyfile(asset.asset_file.name, temp_file_path) 
        
        self.apk_path = temp_file_path
        self.apk_file = apk.APK(self.apk_path)

    def handle_package(self):

        self.app.version = self.apk_file.get_androidversion_name()
        self.app.name = self.apk_file.package
        self.hax_save_icon_file()
        self.app.save()
        
    def hax_save_icon_file(self):

        temp_file, temp_file_path = mkstemp()
        temp_file = open(temp_file_path, "w")

        icons = [{'size' : len(self.apk_file.get_file(x)), 'file' : self.apk_file.get_file(x)} for x in self.apk_file.files if "ic_launcher" in x] #TODO 
        icons = sorted(icons, key=lambda x: x['size'])
        largest_icon_data = icons[-1]['file']
        temp_file.write(largest_icon_data)
        temp_file.close()
        self.app.icon = File(open(temp_file_path, "r"))

    def save_icon_files(self):

        temp_decoded = "%s/app" % self.temp_dir

        os.system("%s/apktool d %s %s" % (settings.UTILITIES_ROOT, self.apk_path, temp_decoded))

        xml = minidom.parse("%s/AndroidManifest.xml" % temp_decoded)
        application_node = xml.getElementsByTagName("application")[0]

        icon_from_xml = application_node.attributes['android:icon'].value
        icon_from_xml = icon_from_xml.replace("@", "")

        resource_dir = "%s/res" % temp_decoded
        matching_dirs = ["%s/%s" % (resource_dir, x) for x in os.listdir(resource_dir) if re.match(icon_from_xml.split("/")[0], x)]

        for d in matching_dirs:

            matching_files = ["%s/%s" % (d, x) for x in os.listdir(d) if re.match("%s.png" % icon_from_xml.split("/")[-1], x)]

            if len(matching_files) > 0:
                [shutil.move(the_file, "%s/%s.png" % (settings.MEDIA_ROOT, self.uuid)) for the_file in matching_files]



class iOSPackageHandler(object):

    def __init__(self, asset):

        self.ipa_asset = asset
        self.ipa_file = ZipFile(self.ipa_asset.asset_file.path) 
        self.temp_dir = mkdtemp()
        self.ipa_file_path = self.ipa_asset.asset_file.path
        self.ipa_plist = self.plist_from_ipa()
        self.app = asset.app

    def handle_package(self):

        self.save_icon_files()

        self.app.version = self.ipa_plist['CFBundleVersion']
        self.app.name = self.ipa_plist['CFBundleName']
        self.app.device_type = "IOS"
        self.app.save()

    def extract_app_name(self): 

        filelist = self.ipa_file.filelist
        regex = re.compile(".*\.app/$")
        app_name = "".join([thefile.filename for thefile in filelist if regex.match(thefile.filename)][0].split(".")[0:-1][0].split("/")[-1])

        return app_name

    def extract_uuid(self):

        """
        Dwarfdump doesn't work on other systems, we might bring this back later but it's not super important
        right now seeing as there isn't any crash reporting going on.

        app_name = self.extract_app_name()
        app_binary_location = self.ipa_file.extract("Payload/%s.app/%s" % (app_name, self.ipa_plist['CFBundleExecutable']), path=self.temp_dir)
        dump_handle = os.popen("dwarfdump --uuid %s" % app_binary_location)
        uuid = dump_handle.read().split(' ')[1]
        dump_handle.close()
        """

        uuid_string = x = uuid1().hex
        uuid = "%s-%s-%s-%s-%s" % (x[0:8], x[8:12], x[12:16], x[16:20], x[20:32]) 


        return uuid

    def save_icon_files(self):

        icons = []

        if 'CFBundleIconFiles' in self.ipa_plist.keys():
            icons = self.ipa_plist['CFBundleIconFiles']
        elif 'CFBundleIcons' in self.ipa_plist.keys():
            icons = self.ipa_plist['CFBundleIcons']['CFBundlePrimaryIcon']['CFBundleIconFiles']

        if len(icons) > 0:

            hires_search_pattern = re.compile(".*@2x.png")
            hires_icons = filter(hires_search_pattern.match, icons)
            if len(hires_icons) < 1:
                icon = icons[0]
            else:
                icon = hires_icons[0]
            icon_search_pattern = re.compile(".*%s" % icon)
            icon_path = [f.filename for f in self.ipa_file.filelist if icon_search_pattern.match(f.filename)][0] 
            extracted_icon_path = self.ipa_file.extract(icon_path, path=self.temp_dir)
            updatePNG(extracted_icon_path)

            image = File(open(extracted_icon_path))
            self.app.icon = image

    def plist_from_ipa(self):

        app_name = self.extract_app_name()
        plist_dict_path = self.ipa_file.extract("Payload/" + app_name + ".app/" + "Info.plist", path=self.temp_dir)

        parsed_dict = biplist.readPlist(plist_dict_path)
        copied_dict = dict(parsed_dict)

        return copied_dict

    def decode_crash_report(raw_crash_report):

        if os.path.isfile("%s/plcrashutil" % settings.UTILITIES_ROOT) == False:
            raise IOError("Could not file plcrashutil in your UTILITIES_ROOT defined in settings.py")
        if os.path.isfile(raw_crash_report) == False:
            raise IOError("Could not find crash report '%s'." % raw_crash_report)

        
        temp_crash_loc = mkstemp()[1]

        os.system("%s/plcrashutil convert --format=ios %s > %s 2> /dev/null" % (settings.UTILITIES_ROOT, raw_crash_report, temp_crash_loc))

        temp_crash_rep = open(temp_crash_loc, "r")

        return (temp_crash_rep, temp_crash_loc)

    def symbolicate_crash(crash_json, dsym_zip_location, ipa_location):


        the_zip = ZipFile(dsym_zip_location)
        the_ipa = ZipFile(ipa_location)

        temp_location = mkdtemp()

        the_zip.extractall(path=temp_location)
        the_ipa.extractall(path=temp_location)

        rx = re.compile("^(.*DWARF/$)")
        dsym_dir = [x.filename for x in the_zip.filelist if rx.match(x.filename)][0]

        rx = re.compile("Payload/(.*).app/")
        binary_dir = [x.filename for x in the_ipa.filelist if rx.match(x.filename)][0]

        temp_dsym_path = temp_location + "/" + dsym_dir
        temp_ipa_path = temp_location + "/" + binary_dir

        temp_symd = mkstemp()[1]

        export_cmd = "export DEVELOPER_DIR=`xcode-select --print-path`;"
        sym_cmd =  "%s/symbolicatecrash -v -o %s %s %s %s" % (settings.UTILITIES_ROOT, temp_symd, crash_report, temp_dsym_path, temp_ipa_path)
        print sym_cmd
        os.system(export_cmd + sym_cmd)

        symd_crash = open(temp_symd, "r")

        return (symd_crash, temp_symd)

