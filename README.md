----------
# Spout
Spout is a method of enterprise and beta distribution of iOS and Android apps.  It is written in Python and uses
the Django web framework.

## Installation

First, instantiate a virtualenv (http://pypi.python.org/pypi/virtualenv) on the Spout directory.
All dependencies are included in this repo under the requirements.txt file.  Run pip install -r requirements.txt
to get the dependencies needed.  You then can configure the app just like you would any other Django app.

##Using Spout

###Adding apps
After you have successfully configured and launched Spout, you can start hosting apps for distribution. First, you need to create a product entry in the admin panel.  Go to http://[spout url]/admin to get to the admin panel.  Click the plus button on the main admin page next to Products.  Just add the name of the product that you're going to upload apps for and save.

###Products

Products are the broadest category for your app.  Think of a product as a single listing in the app store.  Products don't include the beta versions of your app, different versions of your app with different configurations, or the like.  You should categorize your apps that fall under those criteria with **tags**.

###Tags

Tags are the "sub-versions" of products that you want to make available to users.  Examples of tags could be branch names, versions specifically created with a certain server configuration, version A/B, etc.  Tags are particularly convenient because when uploading your app using the upload API, tags not found are automatically created.  This is useful when, for example, your build system builds each development branch and pushes to Spout using the upload API, tagging each build with the built branch name.

###Pages

Pages are the views that you create to display apps to your users.  You can specify a product to make available for download, as well as apps tagged a certain way.  

On the "add page" view of the admin console, there are several options to control access to a page you want to create.

 - Title
 - Sub heading
 - HTML To be displayed at the top of your page
 - Public (open to unauthenticated users)
 - Page expiration date
 - How the page should be grouped
 - The rows that make up the page

##User Management

Spout allows you to tightly control what pages your users have access to and for how long their login information is valid.  This is useful when you want to do a limited availability beta test and to ensure that certain users are only able to download apps from specific pages.

###User Admin View
When adding/editing a user, there's several fields you can use to limit access to users.

| Field | |
|----|----|
|Allowed Pages | These are the pages that the user will have access to.  All allowed pages will be displayed in the top area of the user-facing page after the user logs in.|
|Main Page | This is the main page that the user will see after logging in to the site.  Currently, this page also must be listed in the 'Allowed Pages' list as well.|
| Is Admin | Indicates that the user has access to this admin console.|
| Expiration Date | Specifies the time at which the user's account will no longer be active and unable to download apps from allowed pages.|
 
##Upload API

To upload your built apps from Jenkins or Travis CI, you can use one of two upload APIs.

###Simple Upload API
This API should be used when you only have one build artifact to upload and you are creating the app for the first time on Spout.  This API uses a POST to the `/upload` endpoint using the following parameters:

| Parameter        | Description           |
| ------------- |-------------|
| product | Product name (case insensitive) |
| app_package | Binary app file |
| file_type | Specify either IOS or ANDROID |
| note | Notes about this build |
| tag | The single tag that you want to apply to this app |

###Advanced Upload API

You should use the advanced upload API when you have multiple assets (perhaps an .ipa file and a .dSYM file) that you want to upload and be attached to the app.  You must first create the app by POSTing to the `/app/create` endpoint using the following parameters:

| Parameter |  |
|----|----|
| product | Product name (case insensitive) |
| note | Notes about this app |
| tags | Comma separated list of tags to apply to this app.  If the tag doesn't exist, it is created.|

Upon posting successfully, a JSON dictionary is returned:

| Parameter |  |
|---|---|
| app_id | The newly created app ID |

Once you have the app ID, you can post to the endpoint `/app/[app id]/asset/add` to add any number of assets to be associated with your app.  POSTing to this takes the following parameters:

| Parameter |  |
|---|---|
| primary | 1 or 0 if the app should be considered the primary asset associated with the app.  Typically, primary assets would be the app binary (.apk or .ipa file).|
| asset_file | The binary file to associate with the app |


##Site Settings

Your current site is typically the first one listed (with ID 1) in the Sites list on the admin page.

###S3 Upload Settings
Spout can take your builds and upload them automatically to S3.  In the site configuration view, click "Upload builds to S3" and enter your S3 bucket name as well as your AWS access credentials.


## Local Development

If you are going to use Sqlite3 for your local development database, be sure to run `pip install pysqlite`.  
Otherwise you may get a rather cryptic error stating that Django cannot load one of its components (because loading the database engine didn't work),
though no helpful error message is shown.
