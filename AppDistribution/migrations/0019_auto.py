# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding M2M table for field assets on 'AssetType'
        db.create_table(u'AppDistribution_assettype_assets', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('assettype', models.ForeignKey(orm[u'AppDistribution.assettype'], null=False)),
            ('appasset', models.ForeignKey(orm[u'AppDistribution.appasset'], null=False))
        ))
        db.create_unique(u'AppDistribution_assettype_assets', ['assettype_id', 'appasset_id'])

        # Removing M2M table for field asset_type on 'AppAsset'
        db.delete_table('AppDistribution_appasset_asset_type')


    def backwards(self, orm):
        # Removing M2M table for field assets on 'AssetType'
        db.delete_table('AppDistribution_assettype_assets')

        # Adding M2M table for field asset_type on 'AppAsset'
        db.create_table(u'AppDistribution_appasset_asset_type', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('appasset', models.ForeignKey(orm[u'AppDistribution.appasset'], null=False)),
            ('assettype', models.ForeignKey(orm[u'AppDistribution.assettype'], null=False))
        ))
        db.create_unique(u'AppDistribution_appasset_asset_type', ['appasset_id', 'assettype_id'])


    models = {
        u'AppDistribution.app': {
            'Meta': {'object_name': 'App'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'device_type': ('django.db.models.fields.CharField', [], {'default': "'IOS'", 'max_length': '255'}),
            'download_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['AppDistribution.Product']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'apps'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['AppDistribution.Tag']"}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'AppDistribution.appasset': {
            'Meta': {'object_name': 'AppAsset'},
            'app': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assets'", 'null': 'True', 'to': u"orm['AppDistribution.App']"}),
            'asset_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'AppDistribution.assettype': {
            'Meta': {'object_name': 'AssetType'},
            'assets': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'asset_type'", 'symmetrical': 'False', 'to': u"orm['AppDistribution.AppAsset']"}),
            'extension': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'AppDistribution.page': {
            'Meta': {'object_name': 'Page'},
            'expiration_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'group_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'heading': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'requires_auth': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'top_html': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'AppDistribution.pagerow': {
            'Meta': {'object_name': 'PageRow'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['AppDistribution.Page']"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['AppDistribution.Product']"}),
            'show_options': ('django.db.models.fields.BigIntegerField', [], {'default': 'None'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['AppDistribution.Tag']", 'null': 'True', 'blank': 'True'})
        },
        u'AppDistribution.product': {
            'Meta': {'object_name': 'Product'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'AppDistribution.setting': {
            'Meta': {'object_name': 'Setting'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'value_type': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'AppDistribution.spoutsite': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'SpoutSite'},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'home_page': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['AppDistribution.Page']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'AppDistribution.spoutuser': {
            'Meta': {'ordering': "['username']", 'object_name': 'SpoutUser'},
            'allowed_pages': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'user_allowed_pages'", 'null': 'True', 'to': u"orm['AppDistribution.Page']"}),
            'email': ('django.db.models.fields.EmailField', [], {'db_index': 'True', 'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'expiration_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'main_page': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'users'", 'null': 'True', 'to': u"orm['AppDistribution.Page']"}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'AppDistribution.tag': {
            'Meta': {'object_name': 'Tag'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['AppDistribution']