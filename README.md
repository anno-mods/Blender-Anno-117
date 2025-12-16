# Blender Addon for Anno 117
Blender addon to work with Anno 117 graphics assets. 

- Import/Export of 117 graphics files (.cfg) 
- Import/Export of .rdm meshes (powered by rdm4)
- Import/Export of feedback files (.fc)

# Requirements
- Blender **4(.2)** https://www.blender.org/
- [rdm4](https://github.com/lukts30/rdm4)
- [texconv](https://github.com/microsoft/DirectXTex)
- [filedbreader](https://github.com/anno-mods/FileDBReader)

# Installation
1. Install the other tools.
2. Download the addon. For this, click on the green <>Code Button on this github page and select download zip. Alternatively, use this link https://github.com/anno-mods/Blender-Anno-117/archive/refs/heads/main.zip Extract the zip file and look for the folder io_annocfg inside it. Zip that folder.
3. Open blender, go to Edit->Preferences->Addons. Click `Install...` and select the created `io_annocfg.zip`
4. If you haven't done so already, **unpack the .rda files** (at least the data/graphics part of it) into a single folder. It should look something like this: `C:\whatever\somewhere\rda\data\graphics\...`.  
5. In the addon preferences, set the **rda path** to the folder that **contains** your `data` folder with the unpacked rda files. In this example, that would be `C:\whatever\somewhere\rda`
6. Specify the paths to the `texconv.exe`, `rdm4-bin.exe`, `FileDBReader.exe` executables.
7. I recommend that you enable caching and set the cache probability to 100%. This will require quite a lot of extra hard disk space, but will make handling FILE_ objects much easier, as they will be represented with instanced collections (-> it's not possible to accidentally select an object inside the file instead of the FILE object). Also, it should improve loading speed. See "Asset library" for further details.

# Usage
## Importing 
1. With the addon enabled, go to `Blender->Import->Anno 117 (.cfg)`. Select the .cfg file that you want to import into blender. 
2. This may take some time. Tip: Use solid viewport shading during the import - generating the material shaders takes up the most time. 
3. It should look something like this now:
4. ![Blender 08_01_2022 23_04_29](https://user-images.githubusercontent.com/94999291/148661492-a38178c6-9e5f-49b2-9c3f-404f283c21a0.png)

If you don't want to import from the rda directory, but from a mod folder, set the Anno Mod Folder (under Anno Scene) to your mod folder first. This allows the addon to also consider the files inside that folder.


## Editing
First a few words to the scene structure. Your imported object is called MAIN_FILE_* and all other objects are (in)direct children of it, corresponding to the tree structure of the .cfg xml. Furthermore, the main file has two special children, the IFOFILE (blocking) and the CF7FILE (animated stuff), if you imported these files. 
Each object in the scene starts with some capitalized identifier (its config type). The name does not determine the ConfigType though, it is just for clarity.
The hierarchy corresponds to the XML hierarchy and is  therefore important.

With "N", you can show/hide a properties window in the 3D View. There, select "Anno Object" to get more details on each object. 

You can:
- Reposition models, dummies etc to your liking. Or duplicate or delete them.
- Edit meshes. When done, keep the Model selected and go to Export->Anno Model (.rdm, .glb). You can directly safe it as .rdm. Please export it to a subfolder of the rda folder or your scenes mod folder. I suggest to use `Ctrl+A->All Transforms` before exporting.
- Edit the properties in the Anno Object Tab.
- Change material texture files - but make sure that the texture path is a subpath of either the rda folder or your current mod directory, otherwise the addon cannot convert the path to a relative /data/graphics/... path. The same goes for FileNames of other objects. If you want to add new materials, you need to duplicate existing materials imported from .cfg files and use that one. Otherwise it will lack important xml entries and will not work in the game itself.
- Add subfiles by importing another .cfg file while the MAIN_FILE is selected and using the option "import as subfile".
- Regarding the .ifo objects: There are two types of ifo objects. Cubes and Planes. Cubes: Move them around, scale them, rotate them. Edit mode modifications do not work for these. IfoPlanes can be edited in edit mode (and object mode, if you want). This is because for planes, the individual vertex positions are important, for cubes its just about the boundaries.
- If you want to add some assets from another .cfg file, simply import both. Then you change the parent to bring them into the other file.
Tip: The .ifo and .cf7 objects might be distracting. If you shift click on the eye next to the IFOFILE or CF7FILE object in the scene tree view, you can hide them all.

## Exporting
0. If you edited models, you must export them to .rdm first. (This automatically adapts their FileName to your export location).

1. Select your MAIN_FILE object.
2. Go the Export->Anno (.cfg) and select where you want to export to. 
3. The exporter will create the .cfg (and .ifo and .cf7) file(s).

## Feedback
When you've imported a .cf7 file, you'll get a CF7FILE Object. In its properties, you basically get the whole xml document (except for the dummies). You can edit the values there. But due to blender ui scripting limitations, you cannot add or remove any nodes here. :-( But wait, cf7 is a terrible format for Feedback Definitions anyways, right? 
You might have noticed that the import/export tools allow you to change from .cf7 to SimpleAnnoFeedbackEncoding. Please don't use this as it doesn't work for Anno 117 yet.

# Asset Library
## Setup 
To set up  the asset library, create a fresh .blend file. Click the `File->Import Anno Cfg Asset` button. The addon will now load *all* .cfg files located somewhere in the selected folder (which needs to be somewhere inside your rda folder). This will take a long time (go for a walk, watch a movie, sleep). After that save this .blend file in a user-library directory. The default one is `C:\Users\<USERNAME>\Documents\Blender\Assets` (but you can add more in the blender preferences). Now every cfg is marked as an asset and tagged with more or less useful tags.

You might also want to have other objects in your asset browser. 
If you want f.e. to use all the models you made somewhere in all your project files, just save all your .blend files in the same user-library directory and mark the models you want as assets. I'd suggest to add a duplicate of them that has no parent object as asset (to avoid confusion). So you can just extract all kinds of nice parts from the vanilla models, save them in your asset library and then use them whereever you want. 

Note that when you drag a .cfg asset into your scene, it will be an *instanced collection*, i.e. looking great but totally useless for modding.
There are two options to make them useful:
- You convert it into a FILE object using `Instanced Collection To FILE_` in the anno object tab. It will be an empty that behaves like a file object, so you can parent it to a main file. You can however not edit it, nor can you load its animations.
- You make the instanced collection *real*. You can either use `Object->Apply->Make Instances Real` (with the keep hierarchy setting active) or just use the button `Make Collection Instance Real`, located in the Anno Object tab. After that, you'll get a `File` object that you can parent to some other main file or edit.

It is noteworthy that if you enable caching and the first import produced wrong results for some reason, all subsequent imports will have the same mistake. In case you think that something is wrong or if the .cfg have changed (for example due to a patch), delete all contents of the cache folder.

## Usage
Now you can use this library in other .blend files. For this, open the asset browser and select the user library you used. Drag and drop the assets into your scene. 

# Troubleshooting
The anno files are complicated and things can go wrong, here's how to figure out what's wrong.

When the imported file does not look like you expected, have a look at the console `Window->Toggle System Console` and scroll through. If the tool wasn't able to locate textures or models or if the conversion from rdm to glb using rdm4 failed, you'll see these things here.

If you get an parsing error that means that something is wrong with one of the imported .cfg/.cf7/.ifo files and this caused the xml parser to fail. 

If you are unsure if the export worked properly, try importing your exported file. If it doesn't look identical, something went wrong. Make sure that the object parent hierarchy is valid, if some objects do not show up in your imported file.

For materials, its important to not have any standard blender materials on your models, otherwise the export will fail. You'll need to use an imported material - only those have the specific custom properties and correctly named shader nodes. Speaking of shader nodes, please note that Cloth materials and Model materials are incompatible. 

There are quite a few weird reason for your model or parts of it becoming invisible in game. Most likely, it's related to something being wrong with the materials. Missing textures (keep in mind that anno needs a `.dds` version of your `.png`file. Also, make sure that your material has the correct vertex format (same as your model, almost always `P4h_N4b_G4b_B4b_T2h`)! Some models (those with animations) have a different vertex format than others. 
Animated models in general are quite tricky and can also cause issues with visibility. If you have animated models in your cfg that you want to use and edit (as a static object), remove all animation entries from the model. Furthermore, go through all Tracks in the AnimatedSequences section and remove all of them that reference this model with the BlenderModelID property. Note that if you want to use edited animated models, that's much more effort and is not directly supported by this tool. I refer you to the rdm4 documentation. 
