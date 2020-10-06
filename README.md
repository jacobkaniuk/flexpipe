![Letterhead](/res/flexpipe_letterhead.png)

<br></br>

**flexpipe** is an open source asset management system. It can be used for the management and tracking of a variety of assets in a VFX, animation and/or games pipeline, whether in a professional production environment or for smaller personal projects at home.

**flexpipe**'s API is built with modularity and flexibility in mind. The goal is to include a lightweight framework in which different tools can be used to help set up a structured workflow in an already existing environment, and tools specific to your production's needs can be easily created and incorporated using the extensible API.

For teams which are working collaboratively, with the majority of members working remotely, the system will have an easy way to get your project's pipeline set up in the cloud.

The system may also be used as an all around solution for smaller teams or studios looking to add a bit more structure to their workflow and content creation process.

API Supported Queries
<h2>Project independant queries</h2>

>Please reference the [documentation](http://github.com/jacobkaniuk/flexpipe/docs) for supported fields and additional arguments

> **get_assets** (general purpose query, takes many different arguments to build results)
> **get_assets_by_project** (return all assets of a certain type from specified project)
> **get_assets_by_shot** (return all assets of this of the specified asset type from a shot)
> **get_assets_by_type** (return assets based on their type/department they're part of)
> **get_user_assets** (return all assets which were published )
> **get_assets_by_database_path** (return all assets from a relative path)


<h3>Examples</h3>

Let's get all of the **Model** assets from a project we're working on
```python
from core_api.manager.asset_manager import AssetReader
from core_api.assets.model_asset import ModelAsset

asset_reader = AssetReader()
project_name = "arch_viz"
model_assets = asset_reader.get_assets_by_project(ModelAsset, project_name)
```

Now let's get all of the **Texture** assets from a project we're working on, but only from the last week
```python
import datetime
from core_api.assets.texture_asset import TextureAsset

asset_reader = AssetReader()
project_name = "arch_viz"
start = datetime.date(2020, 9, 8)
end   = datetime.date.today() #assuming today is September 15 
texture_assets = asset_reader.get_assets(TextureAsset, project_name, from_date=start, to_date=end, representations=True)
```

Let's take all of those **Texture** assets and version them up by **1**
```python
from core_api.publishers.texture_publisher import TexturePublisher
for texture_asset in texture_assets:
    texture_asset.asset_handler.version_up()
```

Damn, all of the **Anim** assets from **Vancouver** that were published last night need to be rolled back to the previous version, they don't seem to be working in the latest layout.
```python
import datetime
from core_api.assets.anim_asset import AnimAsset

start = datetime.date.today()
start = start.replace(day=start.day-1)
end = datetime.datetime.now()

# get all of the Anim assets from Vancouver published from yesterday until now
bad_assets = asset_reader.get_assets(AnimAsset, project="arch_viz", location="Vancouver", from_date=start, to_date=end)

# roll back 1 version, returns a list of the newly updated/rolled back assets
# these will simply create a new version (version_up) using the data from the previous publish
rolled_back = [bad_asset.asset_handler.roll_back(1) for bad_asset in bad_assets]
```

>**Asset types and usage**

|Examples|ModelAsset|ImageAsset|TextureAsset|AnimAsset|LightingAsset|RigAsset|SceneAsset|FXAsset|
|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
**Usage Examples**| Polygonal or NURB data displayed as 3D objects in a scene|Reference images, screengrabs, plate, luts|Textures used in model asset materials/shaders or environmnets|Scene data for animated rig assets |Light rigs used in layout files to light the scene for rendering  |Rigged model assets used by animators to create animations |Scenes containing other asset types which get all| Various types of simulation data (hair and fur, destruction, pyro, fluid)
|**File types**|**.fbx, .abc, .obj**|**.png, .jpg, .dpx, .exr**|**.tga, .exr, .tex**|**.ma, .blend, .max**|**.ma, .hda, .max, .blend**|**.ma, .blend, .max**|**.ma, .blend, .max**|**.hip, .ma, .blend, .max**
