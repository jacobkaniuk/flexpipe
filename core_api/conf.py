PUBLISHED_ASSETS = 'published_assets'
ASSETS = 'assets'
SETTINGS = 'settings'
SHOTS = 'shots'
DB_USERS = r"['users']"
PROJECT_USERS = 'users'

ASSET_STATUS = [
    0,      # ready to start/pick up
    1,      # in progress
    2,      # ready for review
    3,      # needs fixes/changes
    4,      # intermediately approved
    5,      # approved
    -1      # omit
]

DEPARTMENTS = {
    'CPT':  'concept',          # concept art for backgrounds, environments, characters
    'STRY': 'storyboard',       # storyboards for previs and tracking dept to use as base
    'ED':   'editorial',        # footage injest/cutting
    'PREV': 'previs',           # previs/animatics of shot sequences
    'TRK':  'tracking',         # 2D/3D tracking of raw plate/footage
    'LAY':  'layout',           # layout of assets in scene
    'MDL':  'modeling',         # 3D models of assets which will populate scenes/shots
    'TEX':  'texturing',        # image textures which will be applied to models
    'LKDV': 'lookdev',          # material development for textures on models
    'RIG':  'rigging',          # rigging of 2D/3D assets
    'ANIM': 'anim',             # animation of 2D/3D assets
    'LGHT': 'lighting',         # setting up scenes with lights and render settings
    'COMP': 'comp',             # compositing of rendered sequences/plate
    'DI':   'di'                # digital intermediate (usually final prep for client)
}

MULTI_DEPT = {
    'DESIGN':   {DEPARTMENTS['CPT'], DEPARTMENTS['STRY'], DEPARTMENTS['PREV']},
    'TRACKING': {DEPARTMENTS['PREV'], DEPARTMENTS['TRK'], DEPARTMENTS['LAY']},
    'ASSETS':   {DEPARTMENTS['MDL'], DEPARTMENTS['TEX'], DEPARTMENTS['LKDV']},
    'ANIM':     {DEPARTMENTS['RIG'], DEPARTMENTS['ANIM']},
    'FINAL':    {DEPARTMENTS['LGHT'], DEPARTMENTS['COMP'], DEPARTMENTS['DI']}
}

ASSET_PREFIX_TYPES = {          # Examples
    'STRUC': 'structural',      # road chunks, bridge chunk, building beams, sidewalk
    'VHCL': 'vehicle',          # car, truck, boat, airplane, train
    'MACH': 'machinery',        # forklift, bobcat, conveyor belt, factory system equipment
    'VEG': 'vegetation',        # tree, cactus, flowers, shrub, leaves, bush, stones
    'UTIL': 'utilities',        # telephone wires, street lights, traffic lights, power generator box
    'CHAR': 'character',        # human, humanoid
    'CRE': 'creature',          # wolf, bear, dragon, cyclops, zombie
    'BLD': 'building',          # skyscraper, house, cottage
    'DECO': 'decoration',       # litter, pop cans, newspaper, flyers, cups, pans, set decoration
    'MISC': 'miscellaneous'     # add more types/use this if asset doesn't fall into any category above
}