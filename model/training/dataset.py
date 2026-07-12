import os
import json
import random

MINERAL_REGISTRY = {
    "azurite": {
        "mineral_name": "Azurite",
        "chemical_formula": "Cu3(CO3)2(OH)2",
        "usual_forming_spots": [
            "Oxidized zones of copper ore deposits",
            "Hydrothermal veins embedded in limestone environments",
            "Weathered outcrops containing primary copper sulfides"
        ],
        "colour": ["Deep blue", "Azure", "Dark indigo"],
        "geometrical_shape": [
            "Flat tabular crystals or chunky blocks",
            "Rounded bubble-like clusters",
            "Groups of short, blocky prisms",
            "Crusty coatings and rough, bumpy masses"
        ],
        "luster": [
            "Glassy and highly reflective",
            "Shiny like clean glass",
            "Bright, glass-like shine",
            "Slightly duller than a gemstone but still very glassy"
        ],
        "hardness": {
            "mohs_scale": "3.5 - 4.0",
            "field_test": "Cannot be scratched by a copper penny, but a pocket knife or steel nail scratches it easily."
        }
    },
    "baryte": {
        "mineral_name": "Baryte",
        "chemical_formula": "BaSO4",
        "usual_forming_spots": [
            "Low-temperature hydrothermal veins",
            "Sedimentary bedded deposits as a precipitate",
            "Residual weathering clays and limestone cavities"
        ],
        "colour": ["White", "Colorless", "Pale yellow", "Light blue", "Grey"],
        "geometrical_shape": [
            "Flat bladed crystals stacked together",
            "Petal-like structures that look like a desert rose",
            "Thin, overlapping crystal flakes",
            "Heavy, compact, blocky crystals"
        ],
        "luster": [
            "Glassy with a pearly sheen on the flat sides",
            "Glass-like but slightly milky",
            "Pearly and soft shine",
            "Slightly greasy or pearly surface reflection"
        ],
        "hardness": {
            "mohs_scale": "3.0 - 3.5",
            "field_test": "Can be scratched by a pocket knife; a copper penny may slightly scratch it if firm pressure is applied."
        }
    },
    "beryl": {
        "mineral_name": "Beryl",
        "chemical_formula": "Be3Al2Si6O18",
        "usual_forming_spots": [
            "Granitic pegmatites",
            "Mica schists",
            "Hydrothermal veins associated with tin and tungsten ores"
        ],
        "colour": ["Emerald green", "Aquamarine blue", "Yellow", "Pink", "Colorless"],
        "geometrical_shape": [
            "Long, distinct six-sided columns",
            "Hexagonal rods with flat ends",
            "Pencil-shaped six-sided prisms",
            "Elongated hexagonal columns sticking out of rock"
        ],
        "luster": [
            "Brilliant glass shine",
            "Glassy and translucent",
            "Bright, gem-like glassy reflection",
            "Shiny like glass, sometimes slightly resinous or waxy"
        ],
        "hardness": {
            "mohs_scale": "7.5 - 8.0",
            "field_test": "Extremely hard. Easily scratches glass and quartz crystals; completely unaffected by steel files or knives."
        }
    },
    "calcite": {
        "mineral_name": "Calcite",
        "chemical_formula": "CaCO3",
        "usual_forming_spots": [
            "Sedimentary limestone and marble formations",
            "Hydrothermal vein pathways",
            "Cave systems as stalactites and stalagmites"
        ],
        "colour": ["Colorless", "White", "Yellow", "Orange", "Pale pink", "Grey"],
        "geometrical_shape": [
            "Slanted blocks that look like a leaned cube",
            "Pointy, tooth-like crystal clusters",
            "Rhombohedral box shapes and skewed blocks",
            "Grainy, massive blocky aggregates"
        ],
        "luster": [
            "Glassy, turning into a pearly shimmer on split surfaces",
            "Shiny like glass",
            "Glass-like surface, occasionally looks a bit pearly",
            "Vitreous and reflective"
        ],
        "hardness": {
            "mohs_scale": "3.0",
            "field_test": "A copper penny will easily leave a distinct scratch/groove on its surface. Your fingernail will not scratch it."
        }
    },
    "cerussite": {
        "mineral_name": "Cerussite",
        "chemical_formula": "PbCO3",
        "usual_forming_spots": [
            "Oxidized zones of lead ore deposits",
            "Weathering profiles of primary galena vein structures"
        ],
        "colour": ["Colorless", "White", "Grey", "Smoky yellowish-brown"],
        "geometrical_shape": [
            "Criss-crossing lattice structures that look like a web",
            "Thin plates twinned together into star shapes",
            "Flat, heavy tabular blades",
            "Clusters of needle-like or fibrous structures"
        ],
        "luster": [
            "Brilliant and diamond-like shine",
            "Superlative glassy sparkle, almost like a gemstone",
            "Adamantine, highly reflective and bright",
            "Very shiny, turning slightly greasy on broken edges"
        ],
        "hardness": {
            "mohs_scale": "3.0 - 3.5",
            "field_test": "Relatively soft despite its heavy weight. Easily scratched by a pocket knife or a steel nail."
        }
    },
    "copper": {
        "mineral_name": "Native Copper",
        "chemical_formula": "Cu",
        "usual_forming_spots": [
            "Zones of oxidized copper veins",
            "Cavities of basaltic lavas and volcanic rocks",
            "Hydrothermal reduction zones"
        ],
        "colour": ["Copper red", "Muted metallic brown", "Weathered dull green (tarnish)"],
        "geometrical_shape": [
            "Branching, tree-like metal veins",
            "Irregular jagged lumps and nuggets",
            "Wire-like twisting threads",
            "Dendritic root-like patterns spread over rock"
        ],
        "luster": [
            "Bright, polished metal shine",
            "Metallic, looking like raw old copper coins",
            "Dull metal appearance when tarnished",
            "Strongly metallic and reflective"
        ],
        "hardness": {
            "mohs_scale": "2.5 - 3.0",
            "field_test": "Malleable. Can be scratched or carved into by a pocket knife, and can be slightly scratched by a copper penny."
        }
    },
    "fluorite": {
        "mineral_name": "Fluorite",
        "chemical_formula": "CaF2",
        "usual_forming_spots": [
            "Hydrothermal veins traversing granite or limestone",
            "Sedimentary dolostone cavities",
            "Geodes and alpine fissures"
        ],
        "colour": ["Purple", "Green", "Yellow", "Clear", "Deep blue", "Magenta"],
        "geometrical_shape": [
            "Perfect geometric cubes",
            "Double-pyramid shapes joined at the base",
            "Interlocking boxy clusters",
            "Sharp cubic corners and blocky clusters"
        ],
        "luster": [
            "Clean glass shine",
            "Glassy and crisp",
            "Vitreous, brightly reflecting light like glass",
            "Smooth and glassy surface appearance"
        ],
        "hardness": {
            "mohs_scale": "4.0",
            "field_test": "Easily scratched by a pocket knife or steel nail, but cannot be scratched by a copper penny."
        }
    },
    "gypsum": {
        "mineral_name": "Gypsum",
        "chemical_formula": "CaSO4·2H2O",
        "usual_forming_spots": [
            "Evaporite sedimentary basins",
            "Hot spring deposits",
            "Oxidized sulfide zones where sulfuric acid acts on limestone"
        ],
        "colour": ["White", "Colorless", "Tan", "Pearlescent grey"],
        "geometrical_shape": [
            "Flat sword-like crystals",
            "V-shaped swallow-tail twins",
            "Fibrous, thread-like satin columns",
            "Soft platy sheets and massive chalky blocks"
        ],
        "luster": [
            "Glassy, but soft and silky in fibrous versions",
            "Pearly and shimmering on flat surfaces",
            "Silky with a soft, thread-like sheen",
            "Subdued glass shine, turning pearly"
        ],
        "hardness": {
            "mohs_scale": "2.0",
            "field_test": "Very soft. Can be easily scratched or gouged with a standard fingernail."
        }
    },
    "hematite": {
        "mineral_name": "Hematite",
        "chemical_formula": "Fe2O3",
        "usual_forming_spots": [
            "Banded iron formations (BIFs)",
            "Hydrothermal veins and hot spring pools",
            "Weathering products of iron-rich primary rocks"
        ],
        "colour": ["Metallic steel-grey", "Iron black", "Dull earthy brick-red"],
        "geometrical_shape": [
            "Round, bubbling masses that look like dark kidneys",
            "Thick tabular plates and metallic flakes",
            "Smooth, metallic rounded mounds",
            "Lumpy, non-crystalline earthy chunks"
        ],
        "luster": [
            "Metallic steel shine",
            "Dull and earthy like dry clay",
            "Sub-metallic, like old unpolished cast iron",
            "Highly reflective black metal look"
        ],
        "hardness": {
            "mohs_scale": "5.5 - 6.5",
            "field_test": "Variable. Crystalline forms will scratch window glass and resist knives, while earthy forms can crumble under a knife."
        }
    },
    "malachite": {
        "mineral_name": "Malachite",
        "chemical_formula": "Cu2CO3(OH)2",
        "usual_forming_spots": [
            "Oxidized superficial zones of copper deposits",
            "Limestone fractures acting as copper solution traps"
        ],
        "colour": ["Bright green", "Dark forest green", "Banded emerald green"],
        "geometrical_shape": [
            "Round, grape-like clusters",
            "Velvety carpets of fine needle fibers",
            "Concentric concentric banded rings in cross section",
            "Bumpy, smooth bulbous layers coating rock"
        ],
        "luster": [
            "Silky with a velvety shimmer",
            "Dull and earthy on rough exterior surfaces",
            "Soft, weak glassy shine",
            "Subdued, fiber-like silky appearance"
        ],
        "hardness": {
            "mohs_scale": "3.5 - 4.0",
            "field_test": "A copper penny will not scratch it, but a steel knife blade or heavy iron nail will scratch it easily."
        }
    },
    "pyrite": {
        "mineral_name": "Pyrite",
        "chemical_formula": "FeS2",
        "usual_forming_spots": [
            "Hydrothermal veins",
            "Sedimentary shale and coal beds",
            "Metamorphic schists and contact zones"
        ],
        "colour": ["Pale brass yellow", "Bright gold-reflective"],
        "geometrical_shape": [
            "Perfect geometric cubes with grooved lines",
            "Twelve-sided geometric blocks",
            "Interlocking blocky brass clusters",
            "Sharp cubic crystals grown together"
        ],
        "luster": [
            "Highly reflective metallic glare",
            "Shiny like gold-toned metal",
            "Brilliant, mirror-like metal shine",
            "Polished metal appearance"
        ],
        "hardness": {
            "mohs_scale": "6.0 - 6.5",
            "field_test": "Harder than it looks. Easily scratches window glass; steel pocket knives cannot scratch it, but a heavy-duty file will."
        }
    },
    "pyromorphite": {
        "mineral_name": "Pyromorphite",
        "chemical_formula": "Pb5(PO4)3Cl",
        "usual_forming_spots": [
            "Oxidizing zones of lead veins and mineral deposits",
            "Weathering layers sitting above primary galena zones"
        ],
        "colour": ["Bright green", "Olive green", "Yellowish-orange", "Brown"],
        "geometrical_shape": [
            "Tiny, barrel-shaped hexagonal prisms",
            "Clusters of hollowed-out or hollow-tipped tubes",
            "Branching crusts of tiny hexagonal rods",
            "Moss-like or aggregate crystal steps"
        ],
        "luster": [
            "Resinous like hard plastic or dried sap",
            "Greasy, wax-like shine",
            "Sub-adamantine, quite shiny and bright but oily",
            "Oily or plastic-looking surface"
        ],
        "hardness": {
            "mohs_scale": "3.5 - 4.0",
            "field_test": "Resists a copper penny, but the brittle crystals are easily scratched by a steel pocket knife."
        }
    },
    "quartz": {
        "mineral_name": "Quartz",
        "chemical_formula": "SiO2",
        "usual_forming_spots": [
            "Felsic igneous rocks like granite and pegmatite",
            "Hydrothermal vein networks",
            "Metamorphic quartzites and clastic sedimentary sandstones"
        ],
        "colour": ["Colorless", "White (Milky)", "Purple (Amethyst)", "Smoky brown", "Pink (Rose)"],
        "geometrical_shape": [
            "Six-sided crystal points with pyramid ends",
            "Pointy hexagonal spikes sticking out of a cluster",
            "Massive, irregular jagged chunks with curvy edges",
            "Six-sided prisms with distinct pointed tips"
        ],
        "luster": [
            "Crisp glass shine",
            "Vitreous, highly reflective like a clean window",
            "Glassy, turning slightly greasy on broken surfaces",
            "Bright, clear glass reflection"
        ],
        "hardness": {
            "mohs_scale": "7.0",
            "field_test": "Standard benchmark. Easily cuts deep scratches into window glass and steel; completely unaffected by knives or files."
        }
    },
    "smithsonite": {
        "mineral_name": "Smithsonite",
        "chemical_formula": "ZnCO3",
        "usual_forming_spots": [
            "Weathered and oxidized zones of primary zinc ore blocks",
            "Replacement layers inside sedimentary limestone host formations"
        ],
        "colour": ["Light blue", "Apple green", "Pink", "White", "Brownish-yellow"],
        "geometrical_shape": [
            "Smooth, bubbling masses that look like melted wax",
            "Honeycombed or bone-like dry structures",
            "Grape-like rounded bumpy coatings",
            "Smooth bulbous layers lining rock cavities"
        ],
        "luster": [
            "Pearly or satiny sheen",
            "Subdued glass shine, slightly milky",
            "Soft pearly glow",
            "Vitro-pearly, clean but slightly hazy shine"
        ],
        "hardness": {
            "mohs_scale": "4.0 - 4.5",
            "field_test": "Cannot be scratched by a copper penny, but a pocket knife will scratch it if firm pressure is applied."
        }
    },
    "wulfenite": {
        "mineral_name": "Wulfenite",
        "chemical_formula": "PbMoO4",
        "usual_forming_spots": [
            "Oxidized hydrothermal lead-molybdenum veins",
            "Arid weathering environments of heavy metal complexes"
        ],
        "colour": ["Bright orange", "Deep red", "Honey yellow", "Butter yellow"],
        "geometrical_shape": [
            "Incredibly thin square plates",
            "Razor-sharp square wafer crystals",
            "Thin tabular square blocks layered together",
            "Crisp, wafer-thin square window panes"
        ],
        "luster": [
            "Brilliant resinous shine",
            "Bright like a polished plastic gem or heavy sap",
            "Sub-adamantine, highly reflective and oily",
            "Intense glass-to-greasy luster"
        ],
        "hardness": {
            "mohs_scale": "2.5 - 3.0",
            "field_test": "Very soft and brittle. Can be scratched by a copper penny, and a pocket knife cuts into it effortlessly."
        }
    }
}

def build_vlm_dataset(dataset_dir):
    vlm_dataset = []
    
    # Define your fixed target size per mineral
    IMAGES_PER_MINERAL = 100
    
    # Loop through the folders in the dataset directory
    for folder_name in os.listdir(dataset_dir):
        # Handle case variations (e.g., folder 'azurite' matches key 'Azurite')
        registry_key = next((k for k in MINERAL_REGISTRY if k.lower() == folder_name.lower()), None)
        if not registry_key:
            continue
            
        mineral_data = MINERAL_REGISTRY[registry_key]
        folder_path = os.path.join(dataset_dir, folder_name)
        
        # Skip if path isn't a directory
        if not os.path.isdir(folder_path):
            continue
            
        # 1. Gather and validate all images in this folder
        all_images = [
            img for img in os.listdir(folder_path)
            if img.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
        ]
        
        # 2. Caps the samples at 100, or takes everything if the folder has less
        target_count = min(len(all_images), IMAGES_PER_MINERAL)
        
        # If a folder is completely empty, skip it safely
        if target_count == 0:
            continue
            
        selected_images = random.sample(all_images, target_count)
        
        # 3. Loop through the capped subset
        for img_name in selected_images:
            img_path = os.path.join("data", folder_name, img_name)
            
            # Extract randomized variations of characteristics to keep the model robust
            rand_color = random.choice(mineral_data["colour"])
            rand_shape = random.choice(mineral_data["geometrical_shape"])
            rand_luster = random.choice(mineral_data["luster"])
            rand_spot = random.choice(mineral_data["usual_forming_spots"])
            mohs = mineral_data["hardness"]["mohs_scale"]
            field_test = mineral_data["hardness"]["field_test"]
            
            # 15 distinct, clean phrasing strategies
            user_phrasing = [
                "What mineral is this?",
                "Identify this specimen.",
                "Can you give me the chemical formula of this mineral?",
                "What is the chemical compound profile of this mineral?",
                f"Field notes indicate this has a {rand_luster.lower()} luster. What is it?",
                f"Identify this specimen. Context: It looks somewhat {rand_color.lower()}.",
                f"This sample exhibits {rand_shape.lower()}. What mineral species is this?",
                f"Based on the {rand_color.lower()} coloring and {rand_luster.lower()} look, identify the mineral.",
                f"This mineral sits around {mohs} on the Mohs hardness scale. Provide its name and formula.",
                f"Scratch test results: {field_test} Name this mineral.",
                f"This was collected from {rand_spot.lower()}. Identify the crystal.",
                f"I am cataloging a mineral showing {rand_shape.lower()} with a {rand_color.lower()} shade. What is the classification?",
                f"The specimen shows a {rand_luster.lower()} luster and a hardness of {mohs}. Can you classify it?",
                "Analyze the image and provide the mineral profile.",
                f"Geological Log: Found in {rand_spot.lower()}, displays {rand_shape.lower()}, hardness {mohs}. What is the identity?"
            ]
            
            # Select one target phrasing completely at random
            chosen_prompt = random.choice(user_phrasing)
            
            # Enforce the strict JSON output structure you want the model to learn
            target_response = {
                "mineral_name": mineral_data["mineral_name"],
                "chemical_formula": mineral_data["chemical_formula"]
            }
            
            # Format to a flawless LLaVA v1.5 conversation object
            vlm_dataset.append({
                "id": f"min_{random.randint(100000, 999999)}",
                "image": img_path,
                "conversations": [
                    {"from": "human", "value": f"<image>\n{chosen_prompt}"},
                    {"from": "gpt", "value": json.dumps(target_response, indent=2)}
                ]
            })
            
    return vlm_dataset


def save_vlm_dataset(vlm_dataset, output_file_path="./llava_mineral_train.json"):
    """
    Saves the generated VLM dataset array into a cleanly formatted JSON file
    ready for LLaVA fine-tuning.
    
    Parameters:
    vlm_dataset (list): The dataset list returned from build_vlm_dataset()
    output_file_path (str): File path where the JSON should be written
    """
    if not vlm_dataset:
        print("⚠️ Warning: The dataset list is empty. Nothing to save.")
        return
        
    # Ensure directory path exists before writing file
    output_dir = os.path.dirname(output_file_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created directory: {output_dir}")
        
    try:
        # Write dataset array to JSON file with standard 2-space indentation
        with open(output_file_path, "w", encoding="utf-8") as json_file:
            json.dump(vlm_dataset, json_file, indent=2, ensure_ascii=False)
            
        print("=" * 50)
        print("🎉 DATASET EXPORT COMPLETE")
        print(f"📍 Saved to: {output_file_path}")
        print(f"📊 Total Training Samples: {len(vlm_dataset)}")
        print("=" * 50)
        
    except IOError as e:
        print(f"❌ Error writing dataset file to disk: {e}")
        
        
if __name__ == "__main__":
    # 1. Point to your raw Kaggle image folder structure
    KAGGLE_DATA_DIR = "./data" 
    
    # 2. Compile the image files and prompts into LLaVA format
    print("Processing images and mixing prompt styles...")
    processed_data = build_vlm_dataset(KAGGLE_DATA_DIR)
    
    # 3. Export to a single dataset tracking file
    save_vlm_dataset(processed_data, output_file_path="./llava_mineral_train.json")