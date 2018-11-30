# mePhoto 2 Roadmap

## Import tool

- Should be based on configuration file and/or ...
- ... should accept command line parameters
- better both, command line parameters overriding the ones in the configuration file
- Should allow user custom defined directories structures, file naming scheme

Basically no params should be hard-coded in the scripts

## Web application

In order to view / share picture, a web application is needed (wanted / desirable).

Technology I would like to use: Node.js with Express. Also take a look to Sails.js (maybe that's a overkill).

It should have the following features:

- Photo visualization from user defined folder
  - user defined subfolders organization
  - show pictures in chronological order (ascending and descending)
    - date to be determined by several possible heuristic:
      - exif data
      - file name
      - file datetime
  - URL options for user desired dimensions/cropping/rotations (and other effects?)
    - keep original file
    - smart caching of rendered files
    - [SLIR](https://github.com/lencioni/SLIR) like (kind of)
      - [node jimp](https://www.npmjs.com/package/jimp) for image manipulation?  

- App runnable from local pc:

  e.g. launching `node mephoto -d /path/to/my/pictures -p 8000` will run the application as a web server on port 8000 displaying pictures from folder `/path/to/my/pictures`)
- App installable on production server (in such case the options should only stay in configuration file)
- Responsive interface
- Support for templating
- Support for theming (sets of templates and stylesheets)
- Support for theme options
- Support for automatic slideshow (with pictures pre-caching)
- Support for fullscreen
- Support for special effects (special slideshow transitions or similar)
- Support for sharing (login vs localhost, this is a **BIG topic**, see next section)
  - sharing of 
    - single pictures
    - set of pictures (could just be the same of a)
    - single folder 
    - set of folders
    - albums (see later)
    - collections
  - sharing via (options available on remote server) 
    - (optionally) time limited dedicated URL (secret URL) 
    - social login (google, facebook, twitter, ... other? in this case I mean giving visibility permission to specific users of the social platforms)
    - social media (facebook, twitter, instagram, ... other? in this case I mean publishing )
    - photogallery and slideshow embedding
    - download original picture / download zip (also available on localhost)

- Usage of a NoSQL database should be in principle optional but needed to provide the following special features
  - organize pictures in structures different than folders (e.g.: albums, collection)
  - advanced sharing settings
  - picture's title and caption
  - albums, collections (collections are set of albums)
  - tags
  - comments, likes, views
  - annotations (comments over image)
  - exif data (can be retrieved from picture, but faster if cached in db)
  - option to disable standard navigation per folder if using a database
  - additional photostream visualization (all pictures in reverse chronological order)

  - Possible choices for the backend database:
    - neDB for local development / node app
    - MongoDB for deployment on production webserver
    - see [Camo](https://www.npmjs.com/package/camo) and [NekoDB](https://github.com/cutejs/nekodb) for compatible ODMs, (waterline-mongo and waterline-nedb for sails.js)

- Advanced features (part 1)
  - Rich set of RESTful APIs: to manage all the metadata database (picture captions, albums management, etc.. ), but also pictures cache, pictures editing, etc..)
  - admin interface
  - (inline) image editing (levels corrections, conversions, filters, etc..)
  - image datetime adjustments (timezone corrections, wrong data set in pictures, etc..)

- Advanced features (part 2)
  - video visualization (in browser) conversion to webm? (maybe)
  - panoramic photo (and 360 photo)
  - image watermarking

- Advanced features (part 3)
  - AI for photo selection suggestion

- Advanced features (part 4)
  - Import procedures from other platforms (e.g. Google Photo, Flickr, Facebook, Instagram)

## Permissions

If the application is running on the local machine, no permission checking should be performed (basic standard file system permission however will of course apply).
If the application is deployed on a production Internet accessible webserver then a complex logic of permission checking should be applied.
Since it is probably hard to auto-detect the different cases in a Node.js app, this should be a configuration parameter (or environment variable) to establish that (eg. `LOCAL_ENV=true`, `LOCAL_ENV=false`). In such case, what should be the default?

Permissions should be defined on the following entities:
- entire website
- collections
- albums
- folders
- single pictures

Minimum set of permissions to be defined:
- visibility

Other permissions:
- share (?)
- edit
- delete
- other to be defined

Permission should be inherited, unless the underlying entity defines an exception respect to the parent entity. Album and folders (with folders being filesystem directories) should be considered independent.
However Albums and Pictures can have multiparent, causing complex situation to manage.

Visibility can be:
- public
- groups based (do we need it? how complex is it?)
- user based (we need users and authentication, that would be needed anyway for admin operations)

User and authentication can be:
- locally defined
- defined by external provider, e.g:
  - Google
  - Facebook
  - Twitter
  - Open ID
  - etc..
- guests session based (secret URL sharing)

```
Website
  |
  +- collection 1
  |   |
  |   + album 1.1
  |   + album 1.2
  |   \ album 1.3
  |
  +- collection 2
  |   |
  |   + album 2.1
  |   \ album 2.2
  |
  +- album not in a collection 1
  +- album not in a collection 2
  |
  \ folders hierarchy
     |
     + subfolder 1
     |  |
     |  + subfolder 1.1
     |  + subfolder 1.2
     |  \ subfolder 1.3
     |  
     + subfolder 2
     |  ...
...
```     

With the structure defined above, for instance if the global website defines itself to be public, all entities are public, unless exceptions are defined for each one.
For instance: Website public, Collection 1 visible only for users 1, 2 and 3, Album 1.2 only visible for users 1 and 2, Picture X in Album 1.2 only visible for user 1. 
The system is complex and need to intercept conflicts (for instance Album A only visible to user 1 and 2 and Picture X in Album A only visible to user 3... unless the same picture is also published in another album, or folder, visible to user 3).


## URL router possible schema

### URLs for standard navigation

| route                                                        | meaning   |
|--------------------------------------------------------------|------------------------------------------|
| `/`                                                          | home page: should show what the user decided, depending on options, theme, templates, visibility (could for instance display list of public albums, folders, stream of public pictures... actually visibility should depend on user)  |
| `/<folder>`                                                  | if navigation by folder is enabled, it should show (depending on visibility and user), list of subfolders, stream (what is a stream) of pictures in folder `<folder>`   |
| `/<folder>/<subfolder>`                                      | as above, recursive (depending on visibility and user), list of subfolders, stream of pictures in folder <subfolder> and so on  |
| `/<collection>`                                              | list of albums in a specific collection  |
| `/<album>`                                                   | stream of a picture in album  |
| `/<secreturl>`                                               | alias for an album, with optionally limited time validity, where visibility permission checks are disabled   |
| `/p/<params>/<folder>[/<subfolder>[/...]]/<picture_filename>`| render a picture (or movie) where `<params>` are SLIR like URL parameters for resizing, cropping and other operation on the picture  |
| `/p/<params>/<album>/<picture_id>`                           | as above, but linked to a specific album, picture is identified by the database id rather than the filesystem path   |
| `/p/<params>/<secreturl>/<picture_id>`                       | as above, linked to the aliased album, where visibility permission checks are disabled   |

Every album and every collection should have a [slug](https://en.wikipedia.org/wiki/Clean_URL#Slug) that potentially could collide with folder names. We need to understand if collision can be easily avoided. The problem is that if the user creates a new folder with the same name of an existing album slug... in such case collision cannot be avoided, but can be intercepted.

A solution is to have a different URL prefix to distinguish between albums/collections and folders, e.g.: `/<something>` means that `something` should be considered a folder, while `/a/<something>` means that `something` should be considered an album.

**What is a stream**: to be clarified, could be the list of pictures, paginated or not. The web page could have a paginated view, an infinite scrolling, a mixture of both (like Flickr).

### URLs for special operations (to be done)

```
/auth 

/admin ...
```

### URLs for APIs

**GET Apis**

```
GET /api/folders[/:folder[/:folder[...]]]
GET /api/collections
GET /api/albums[/:collection_id]
GET /api/pictures[/:album_id|/:folder|/notInAlbum|/:tag|/:secreturl]
GET /api/pictureInfo/:pictureId
GET /api/pictureComments/:pictureId
```

**POST Apis**
```
To be done
```

**PUT Apis**
```
To be done
```

**DELETE Apis**
```
To be done
```


## Guideline

Every operation in the interface should have a corresponding API
The idea is to make the APIs the entry point both for the interface itself and for any RESTful client of the application.

The question is... SPA (single page application) or standard application with some usage of the API?


## To be clarified:

  - Support for multiuser / multitenancy ?
    - support for users connections
    - pictures sharing advanced settings
  - Pictures copyright information
