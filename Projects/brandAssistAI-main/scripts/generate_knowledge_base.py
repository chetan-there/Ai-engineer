"""Generate a rich, ORIGINAL knowledge base for the BrandAssist catalog.

All content here is written from scratch for fictional, pseudonymized products.
It is intentionally NOT derived from any real manufacturer manual, so it is safe
to publish. Each product family gets multiple manual-style documents (setup, FAQ,
troubleshooting, error codes, maintenance, safety) so the vector store has real
substance to retrieve over.

Usage:
    python scripts/generate_knowledge_base.py --db-path data/brandassist.db

Then re-ingest Chroma:
    python scripts/ingest_chroma.py
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import date
from pathlib import Path


# Each family is keyed by the base product_id. Variant products (e.g.
# microchef-20l-14) inherit their family's content. {name} is filled per product.
FAMILIES: dict[str, dict[str, str]] = {
    "microchef-20l": {
        "device": "microwave oven",
        "setup": (
            "To set up your {name} for the first time, place the microwave on a dry, level surface with at "
            "least 10 cm of clearance on every side and above for ventilation. Plug it into a grounded wall "
            "outlet; avoid extension cords. Remove all packaging from inside the cavity and confirm the glass "
            "turntable and roller ring are seated in the center recess. Set the clock, then run a one-minute "
            "heating test with a microwave-safe cup of water before first real use. Need help during install? "
            "The control panel test mode confirms the magnetron and turntable motor are working."
        ),
        "faq": (
            "Frequently asked questions for the {name}. Can I run it empty? No, never run the microwave with an "
            "empty cavity as this can damage the magnetron. Which containers are safe? Use microwave-safe glass "
            "or ceramic; avoid metal, foil, and most takeout containers. Why does food heat unevenly? Microwaves "
            "heat from the outside in, so stir or rotate food and use the turntable. Can I defrost? Yes, use the "
            "defrost program by weight. Is the door supposed to feel warm? Slight warmth is normal; excessive heat "
            "is not."
        ),
        "troubleshooting": (
            "{name} troubleshooting by symptom. If the microwave will not heat but the turntable spins and the "
            "light works, the most common causes are a tripped internal thermal fuse, a door switch that is not "
            "engaging, or a failed magnetron; stop use and request service. If the turntable does not spin, check "
            "that the roller ring and glass tray are centered and the coupler is not cracked. If it sparks or arcs, "
            "remove any metal or foil and inspect the waveguide cover for food residue or damage. If buttons do not "
            "respond, unplug for 60 seconds to reset. If it runs but the fix still failed after a reset, the unit "
            "needs a technician."
        ),
        "error_codes": (
            "{name} error codes. E-1 indicates a temperature sensor fault: let the unit cool and retry. E-3 means "
            "the door is sensed open during a cycle: open and firmly close the door. E-5 is a keypad/membrane "
            "fault: unplug for one minute to reset. E-7 signals a magnetron over-temperature condition: stop use "
            "and contact support. A flashing colon means the clock needs to be set."
        ),
        "maintenance": (
            "{name} maintenance and cleaning. Wipe the interior after each use with a damp cloth; for stuck-on "
            "food, microwave a bowl of water with lemon for two minutes to loosen residue, then wipe. Clean the "
            "waveguide cover gently and never remove it. Wash the glass turntable in warm soapy water. Keep door "
            "seals free of crumbs so the door closes flush. Do not use abrasive pads or harsh chemical sprays "
            "inside the cavity."
        ),
        "safety": (
            "{name} safety guidance. Never operate the microwave with a damaged door, bent hinge, or faulty latch, "
            "as this can allow microwave leakage. Do not heat sealed containers, whole eggs, or large amounts of "
            "oil. Superheated water can erupt; place a wooden stick in the cup when boiling water. If you see smoke "
            "or arcing, turn it off and unplug immediately. Keep children supervised and never bypass the door "
            "interlock switches."
        ),
    },
    "wavehub-r5": {
        "device": "wifi router",
        "setup": (
            "To set up your {name}, connect the WAN port to your modem with the supplied Ethernet cable, then "
            "power on and wait about 90 seconds for the status LED to turn solid. Connect a phone or laptop to the "
            "default Wi-Fi network printed on the base label, open the setup portal at the listed address, and "
            "follow the wizard to set your network name, password, and admin login. For best coverage, place the "
            "router in a central, elevated, open location away from metal and microwaves. Need help? The LED guide "
            "on the label maps each light color to a setup state."
        ),
        "faq": (
            "Frequently asked questions for the {name}. What is the difference between the 2.4 GHz and 5 GHz bands? "
            "2.4 GHz reaches farther through walls; 5 GHz is faster at shorter range. How many devices can connect? "
            "Up to 64 simultaneous clients. Can I use it in bridge or access-point mode? Yes, from the advanced "
            "settings. Where is the admin password? On the base label until you change it. Does it support guest "
            "Wi-Fi? Yes, enable a separate guest SSID in the portal."
        ),
        "troubleshooting": (
            "{name} troubleshooting. No internet but the router is on: check that the modem is online, reseat the "
            "WAN cable, and power-cycle the modem and router in order. Wi-Fi keeps dropping: reduce interference by "
            "changing the channel, move the router higher and central, and update firmware. Slow speeds: test with "
            "an Ethernet cable to isolate Wi-Fi, and separate the 5 GHz band for nearby devices. Forgot the admin "
            "password: hold the recessed reset button for 10 seconds to factory reset. If the fix still failed, "
            "collect the LED pattern and contact support."
        ),
        "error_codes": (
            "{name} status indicators. Solid white: healthy and online. Solid amber: connected to the router but "
            "no internet from the modem. Blinking amber: firmware update in progress, do not power off. Solid red: "
            "no WAN link detected, check the modem cable. Blinking red: hardware self-test failure, factory reset "
            "and if it persists, request replacement."
        ),
        "maintenance": (
            "{name} maintenance. Keep firmware current via the auto-update setting for security patches and "
            "stability. Reboot monthly to clear memory. Keep vents dust-free and never stack items on top, as the "
            "router relies on passive cooling. Periodically review connected devices and rotate the Wi-Fi password "
            "if you suspect unauthorized access. Back up your settings before any major firmware upgrade."
        ),
        "safety": (
            "{name} safety guidance. Use only the supplied power adapter; a mismatched adapter can overheat the "
            "unit. Do not cover the router or place it inside an enclosed cabinet. Keep it away from water and heat "
            "sources. If the casing becomes hot to the touch, smells of burning, or the adapter is frayed, unplug "
            "it and stop use."
        ),
    },
    "nimbus-ac-1500": {
        "device": "air conditioner",
        "setup": (
            "To set up your {name} split air conditioner, ensure the indoor unit is mounted level by a qualified "
            "installer and the drain line slopes away for condensate. Insert the supplied batteries in the remote, "
            "power on at the wall, and press Mode to select Cool. Set a target temperature a few degrees below room "
            "temperature and confirm cool air within a few minutes. For first use after install, run Cool mode for "
            "30 minutes to clear residual factory odor. Need help? The remote display shows the active mode and set "
            "temperature."
        ),
        "faq": (
            "Frequently asked questions for the {name}. What does Eco mode do? It widens the temperature band and "
            "softens compressor cycling to save power. Why is there water dripping outside? Condensate drainage is "
            "normal during cooling. What temperature is most efficient? Around 24-26 C balances comfort and energy. "
            "How often should the filter be cleaned? Every two to four weeks in heavy use. Can it heat? Only models "
            "with a heat-pump badge; check the spec label."
        ),
        "troubleshooting": (
            "{name} troubleshooting. Not cooling enough: clean the air filters, close windows and doors, and check "
            "that the outdoor unit is not blocked or in direct heat. Unit runs but blows warm air: the refrigerant "
            "charge or compressor may need service; do not attempt refrigerant work yourself. Water leaking from the "
            "indoor unit: the drain line is likely clogged, clear it gently. Remote not responding: replace "
            "batteries and point directly at the unit. Strange odor: clean the filters and evaporator. If the fix "
            "still failed, book a service visit."
        ),
        "error_codes": (
            "{name} error codes. E1 indicates an indoor temperature sensor fault. E2 signals a freeze-protection "
            "trip from restricted airflow: clean filters and restore airflow. E4 is a communication error between "
            "the indoor and outdoor units: check the interconnecting cable. P1 means high-pressure protection: shut "
            "down and call service. F0 indicates low refrigerant detected: professional service required."
        ),
        "maintenance": (
            "{name} maintenance and cleaning. Remove and rinse the washable filters every two to four weeks and dry "
            "fully before refitting. Wipe the front louver and housing with a soft damp cloth. Keep the outdoor "
            "condenser clear of leaves and debris and ensure airflow around it. At season start, run a short test "
            "in Cool mode. Schedule professional servicing of coils and refrigerant annually for best efficiency."
        ),
        "safety": (
            "{name} safety guidance. Always switch off at the wall before cleaning filters. Never insert objects "
            "into the louvers or fan. Refrigerant handling and any electrical or mounting work must be done by a "
            "certified technician. If you smell burning, see sparks, or the unit trips the breaker repeatedly, stop "
            "use and request service. Keep the remote and batteries away from small children."
        ),
    },
    "thermoboil-k1": {
        "device": "electric kettle",
        "setup": (
            "To set up your {name} electric kettle, rinse the interior, then fill with water to the max line and "
            "boil once, discarding that first boil to remove any manufacturing residue. Always seat the kettle "
            "squarely on its power base and keep the base and connector dry. Fill only between the min and max "
            "marks. Close the lid until it clicks so the auto-shutoff works correctly. Need help? The water-level "
            "window lets you fill precisely without overfilling."
        ),
        "faq": (
            "Frequently asked questions for the {name}. Why does it switch off before boiling? An open lid or a "
            "kettle lifted off the base interrupts the cycle. Can I reboil immediately? Yes, but let it settle a "
            "few seconds so the thermostat resets. Why is there white residue? That is harmless limescale from hard "
            "water; descale regularly. Is the minimum fill important? Yes, boiling below the min line can trigger "
            "dry-boil protection."
        ),
        "troubleshooting": (
            "{name} troubleshooting. Kettle will not turn on: confirm it is fully seated on the base and the outlet "
            "has power. It turns off too early: the lid may be open or limescale is tripping the thermostat, so "
            "descale it. Leaking: do not overfill past the max line and check the lid and spout for buildup; stop "
            "use if the base or cord gets wet. Slow to boil or noisy: heavy scale on the element is the usual cause. "
            "If the fix still failed after descaling, the element or thermostat may need replacement."
        ),
        "error_codes": (
            "{name} indicators. A steady light during heating is normal and turns off at boil. A rapidly flashing "
            "light with no heating indicates dry-boil or overheat protection has tripped: unplug, let it cool for "
            "15 minutes, add water above the min line, and retry. If the light will not illuminate at all, the base "
            "contact or thermal cutoff has likely failed."
        ),
        "maintenance": (
            "{name} maintenance. Descale every few weeks with a water-and-white-vinegar or citric-acid solution: "
            "fill to half, boil, let sit 20 minutes, then rinse thoroughly and boil clean water once. Wipe the "
            "exterior with a damp cloth only. Rinse and dry the removable spout filter. Never immerse the kettle or "
            "its base in water. Empty the kettle between uses to limit scale."
        ),
        "safety": (
            "{name} safety guidance. Use only the base supplied with the kettle. Keep the cord away from the "
            "counter edge and out of children's reach. Do not open the lid while boiling, as escaping steam can "
            "scald. Never fill above the max line; hot water can spit from the spout. Stop use immediately if the "
            "cord, plug, or base shows any damage or moisture."
        ),
    },
    "toastpro-2s": {
        "device": "toaster",
        "setup": (
            "To set up your {name} two-slice toaster, place it on a heat-resistant surface well clear of curtains "
            "and cabinets. Before first use, run one full cycle empty in a ventilated room to burn off "
            "manufacturing oils; a little smoke and odor is normal once. Set the browning dial to a middle setting "
            "for the first slice, then adjust to taste. Make sure the crumb tray is inserted. Need help? The "
            "browning dial increases from light to dark as the number rises."
        ),
        "faq": (
            "Frequently asked questions for the {name}. Why is one side darker? Most toasters toast slightly "
            "unevenly; rotate bread or use the bagel setting. What does the bagel setting do? It heats the inner "
            "elements more. Can I toast frozen bread? Yes, use the defrost button to add time. Why did it stop "
            "early? The cancel button or an empty-slot sensor may have triggered. Is smoke ever normal? Only on the "
            "first empty burn-in cycle."
        ),
        "troubleshooting": (
            "{name} troubleshooting. Lever will not stay down: the toaster is electromagnetic, so confirm it is "
            "plugged into a live outlet, as the lever only latches with power. Toast is too light or too dark: "
            "adjust the browning dial and note that the second batch toasts faster when the unit is warm. Smoke "
            "during use: unplug and remove crumbs from the crumb tray and slots. Uneven toasting: clean the slots "
            "and avoid oversized slices. If the lever still failed to latch after confirming power, the solenoid "
            "needs service."
        ),
        "error_codes": (
            "{name} indicators. The cancel light glows while a cycle is running and turns off when toast pops up. "
            "There are no numeric error codes on this model. A lever that will not latch almost always means no "
            "power at the outlet rather than a fault. Continuous tripping of your breaker indicates an internal "
            "short and the unit should be retired."
        ),
        "maintenance": (
            "{name} maintenance and cleaning. Unplug and cool fully before cleaning. Slide out the crumb tray and "
            "empty it after every few uses to prevent smoke and fire risk. Turn the unplugged toaster upside down "
            "over a sink and shake gently to dislodge crumbs. Wipe the exterior with a damp cloth. Never insert "
            "metal utensils into the slots, even to remove stuck bread."
        ),
        "safety": (
            "{name} safety guidance. Never insert forks, knives, or fingers into the slots; unplug first if bread "
            "is stuck and let it cool. Do not cover the toaster or operate it under cabinets or near flammable "
            "items. Bread can catch fire if left unattended, so stay nearby. Keep the crumb tray clean and in "
            "place. Stop use if the cord is damaged or the unit smells of burning plastic."
        ),
    },
    "breezefan-f7": {
        "device": "fan",
        "setup": (
            "To set up your {name} tower fan, assemble the base as shown so the fan stands stable, then place it on "
            "a flat floor away from foot traffic. Insert the remote battery and power on at the wall. Press the "
            "speed button to cycle through speeds and the oscillate button to sweep the airflow. Set the timer if "
            "you want it to switch off automatically. Need help? The control panel mirrors the remote buttons for "
            "speed, mode, oscillation, and timer."
        ),
        "faq": (
            "Frequently asked questions for the {name}. What do the modes do? Normal is steady airflow, Natural "
            "varies speed like a breeze, and Sleep dims the display and lowers speed gradually. Why is airflow "
            "weaker over time? Dust on the intake grille reduces output; clean it. Can it run all night? Yes, but "
            "using the timer and Sleep mode is recommended. Why won't it oscillate? Check that the oscillation is "
            "enabled and the base is fully assembled."
        ),
        "troubleshooting": (
            "{name} troubleshooting. Fan will not turn on: confirm the plug is firm and try another outlet, and "
            "ensure the base is fully seated as some models have an assembly safety contact. Weak airflow: clean "
            "the rear intake grille where dust collects. Will not oscillate: the oscillation may be off or the "
            "internal gear is obstructed. Rattling or wobble: tighten the base and check for a loose grille. Remote "
            "not working: replace the battery and aim at the panel. If the fix still failed, the motor may need "
            "service."
        ),
        "error_codes": (
            "{name} indicators. The display shows the current speed level and remaining timer hours. There are no "
            "fault codes on this model. A display that lights but a fan that does not spin usually means the rotor "
            "is jammed by dust or an object; unplug and clear it. No display at all points to a power or fuse "
            "issue."
        ),
        "maintenance": (
            "{name} maintenance. Unplug before cleaning. Vacuum the rear intake grille and wipe the housing with a "
            "soft, slightly damp cloth; never let water enter the motor housing. For deeper cleaning, use "
            "compressed air through the grille. Store the fan in a dry place during the off-season and keep the "
            "cord loosely coiled to avoid stress."
        ),
        "safety": (
            "{name} safety guidance. Do not insert fingers or objects through the grille while the fan runs. Keep "
            "the cord clear of walkways. Operate on a stable, level surface so the fan cannot tip. Do not use near "
            "water or in damp bathrooms unless rated for it. Stop use if the cord is damaged or the motor smells "
            "hot."
        ),
    },
    "aeropure-220": {
        "device": "air purifier",
        "setup": (
            "To set up your {name} air purifier, open the front cover and remove the plastic wrap from the new "
            "filter, then refit the filter and cover; the unit will not purify effectively with the wrap on. Place "
            "it on a flat surface with at least 30 cm clearance around the air intake and outlet. Power on and "
            "select Auto mode to let the sensor manage fan speed. After installing a fresh filter, reset the filter "
            "life indicator. Need help? The air-quality light shows current conditions at a glance."
        ),
        "faq": (
            "Frequently asked questions for the {name}. What does Auto mode do? It reads the air-quality sensor and "
            "raises fan speed when particles increase. How often do I replace the filter? Typically every 6 to 12 "
            "months depending on use; the indicator will prompt you. Can I wash the HEPA filter? No, replace it; "
            "only the pre-filter is washable. Why is the air-quality light red? It detected elevated particles, "
            "which is normal during cooking or dust."
        ),
        "troubleshooting": (
            "{name} troubleshooting. Weak airflow or no purification: confirm the filter wrap was removed and the "
            "front cover is fully closed, as a cover switch disables the fan when open. Filter indicator stays on "
            "after replacement: reset it by holding the filter button for five seconds. Persistent odor: the "
            "pre-filter needs cleaning or the main filter is exhausted. Noisy operation: check for a loose cover or "
            "debris on the fan. If the fix still failed, the sensor or motor may need service."
        ),
        "error_codes": (
            "{name} indicators. The air-quality ring shows blue for good, amber for moderate, and red for poor air. "
            "A flashing filter icon means it is time to replace the filter. E1 indicates a sensor fault: wipe the "
            "sensor lens and restart. E2 indicates the fan motor is obstructed or failing: unplug, inspect, and "
            "service if it persists."
        ),
        "maintenance": (
            "{name} maintenance. Vacuum or rinse the washable pre-filter every two to four weeks and dry it fully "
            "before refitting. Replace the main HEPA/carbon filter on schedule and reset the indicator. Gently wipe "
            "the dust sensor lens monthly so readings stay accurate. Keep the intake and outlet free of "
            "obstructions and wipe the housing with a dry cloth."
        ),
        "safety": (
            "{name} safety guidance. Always unplug before opening the cover or changing filters. Do not operate "
            "without a filter installed. Keep the purifier away from water and humid areas and never insert objects "
            "into the outlet. Stop use if the cord is damaged or you notice burning smells, and keep the unit out "
            "of reach of young children."
        ),
    },
    "dustmate-v10": {
        "device": "vacuum",
        "setup": (
            "To set up your {name} cordless stick vacuum, charge the battery fully before first use, either on the "
            "dock or via the charge port until the indicator shows full. Click the wand and floor head onto the "
            "main body until they latch. Press the trigger or power button to start and select the suction level. "
            "Empty the dust bin before it passes the max line. Need help? The battery indicator shows remaining "
            "runtime while in use."
        ),
        "faq": (
            "Frequently asked questions for the {name}. How long does the battery last? Roughly the rated runtime on "
            "low and less on boost mode. Can I use it on carpet and hard floors? Yes, the floor head suits both; "
            "use a lower setting on rugs. Why does suction drop? A full bin or clogged filter is the usual cause. "
            "Can I wash the filter? Yes, rinse and dry it fully. How long to recharge? Several hours from empty."
        ),
        "troubleshooting": (
            "{name} troubleshooting. Low or no suction: empty the dust bin, wash and fully dry the filter, and "
            "check the wand and floor head for clogs. Will not turn on: the battery may be flat or too hot, so let "
            "it cool and recharge. Brush roll not spinning: clear hair and threads wrapped around it. Runs then "
            "stops: a blocked airway triggers thermal protection, so clear the blockage and let it cool. If the fix "
            "still failed, the battery may be at end of life."
        ),
        "error_codes": (
            "{name} indicators. A solid battery light shows charge level during use. A flashing red battery light "
            "means low charge or a thermal cutoff from a blockage: clear airways and let it cool. A flashing "
            "brush-bar light indicates the floor head is jammed: remove and clear it. No lights when charging "
            "points to a charger or battery fault."
        ),
        "maintenance": (
            "{name} maintenance. Empty the dust bin after each use and tap out fine dust. Wash the filter under "
            "cold water at least monthly, never use detergent, and let it air-dry for 24 hours before refitting. "
            "Cut away hair wrapped around the brush roll. Wipe the floor head and wand. Store the vacuum on its "
            "dock in a dry place and avoid leaving the battery fully depleted for long periods."
        ),
        "safety": (
            "{name} safety guidance. Use only the supplied charger; an incorrect charger can damage the battery. Do "
            "not vacuum water, embers, or sharp debris. Do not charge or store the unit in direct heat. If the "
            "battery swells, overheats, or smells, stop use and contact support. Keep fingers clear of the brush "
            "roll while it is running."
        ),
    },
    "sonicbar-s20": {
        "device": "soundbar",
        "setup": (
            "To set up your {name} soundbar, place it centered below your TV and connect it with the supplied HDMI "
            "(ARC/eARC) cable to the matching TV port for the best experience; an optical cable is an alternative. "
            "Power on both devices, set the TV audio output to external or ARC, and select the soundbar input. Pair "
            "the remote and, if desired, connect by Bluetooth from your phone's settings. Need help? The front "
            "indicator shows the selected input and volume changes."
        ),
        "faq": (
            "Frequently asked questions for the {name}. Why no sound over HDMI ARC? Enable HDMI-CEC/ARC in the TV "
            "settings and use the labeled ARC port. Can I connect by Bluetooth? Yes, select Bluetooth input and "
            "pair from your phone. What do the sound modes do? Movie boosts surround, Music balances tone, and "
            "Voice lifts dialogue. Can the TV remote control volume? Usually yes, once HDMI-CEC is enabled. Where is "
            "the subwoofer paired? It auto-pairs on power-up."
        ),
        "troubleshooting": (
            "{name} troubleshooting. No sound: confirm the correct input is selected, the TV output is set to the "
            "soundbar, and the HDMI ARC port and CEC setting are correct. Audio out of sync: enable the audio-sync "
            "or lip-sync adjustment. Bluetooth keeps dropping: move closer, remove obstructions, and re-pair after "
            "clearing the old pairing. Subwoofer silent: re-pair it and check it is powered. Crackling: try a "
            "different cable or input. If the fix still failed, factory reset the soundbar."
        ),
        "error_codes": (
            "{name} indicators. A short LED pulse confirms each remote command. A slowly blinking Bluetooth light "
            "means it is in pairing mode; solid means connected. A blinking subwoofer light means it is searching "
            "for the soundbar; solid means paired. Rapid red blinking indicates a firmware-update or fault state; "
            "power-cycle and, if it persists, contact support."
        ),
        "maintenance": (
            "{name} maintenance. Dust the grille gently with a soft dry brush or cloth; do not push objects through "
            "the speaker mesh. Keep firmware updated through the companion app for codec and stability improvements. "
            "Keep the soundbar and subwoofer ventilated and away from heat. Coil cables loosely to avoid strain on "
            "the connectors."
        ),
        "safety": (
            "{name} safety guidance. Use only the supplied power adapter and route cables so they are not a trip "
            "hazard. Keep the unit away from liquids and do not place drinks on top. Mount it securely if "
            "wall-mounting, using appropriate anchors. Stop use if the adapter or cabling is damaged or the unit "
            "overheats."
        ),
    },
    "blendgo-b2": {
        "device": "blender",
        "setup": (
            "To set up your {name} blender, wash the jar, lid, and blade assembly before first use and dry them. "
            "Seat the jar firmly on the motor base until it locks; many models will not start unless the jar is "
            "correctly seated. Add liquid first, then soft items, then ice or hard items, and never fill past the "
            "max line. Start on low and increase speed. Need help? Pulse gives short bursts for controlled "
            "blending."
        ),
        "faq": (
            "Frequently asked questions for the {name}. Why won't it start? A safety interlock prevents operation "
            "unless the jar and lid are locked in place. Can I blend hot liquids? Only with the lid vent open and "
            "in small batches to release steam. Can I crush ice? Yes, with some liquid and the pulse function. Why "
            "does it leak at the base? The blade gasket may be missing or misaligned. How full can I fill it? Never "
            "above the max line."
        ),
        "troubleshooting": (
            "{name} troubleshooting. Will not turn on: confirm the jar is locked onto the base and the lid is "
            "secured, since the interlock blocks operation otherwise. Motor runs but blades do not turn: the drive "
            "coupling may be worn or the jar is not seated. Leaking from the bottom: reseat or replace the blade "
            "gasket and avoid overfilling. Strong burning smell or it stops mid-blend: thermal protection tripped "
            "from overload, so let it cool 15 minutes and blend smaller batches. If the fix still failed, the "
            "coupling or motor needs service."
        ),
        "error_codes": (
            "{name} indicators. A steady power light shows it is ready. A blinking light with no motor action "
            "usually means the jar or lid is not locked, or thermal protection has tripped after overload: let it "
            "cool and retry. No light at all indicates a power or fuse issue. Repeated thermal trips mean batches "
            "are too large or too thick."
        ),
        "maintenance": (
            "{name} maintenance and cleaning. For a quick clean, add warm water and a drop of dish soap and pulse, "
            "then rinse. Periodically remove the blade assembly and gasket to wash separately, and dry fully before "
            "reassembly. Wipe the motor base with a damp cloth only and never immerse it. Inspect the gasket for "
            "wear and replace it if cracked."
        ),
        "safety": (
            "{name} safety guidance. Keep hands and utensils out of the jar while the motor runs; stop and unplug "
            "before scraping. Always secure the lid before blending. When processing hot liquids, vent the lid and "
            "start slow to avoid pressure buildup. Handle the blades carefully as they are sharp. Stop use if the "
            "base, cord, or coupling is damaged."
        ),
    },
}


# Per-section metadata: (kind, doc_id_prefix, title_suffix)
SECTIONS = [
    ("setup", "manual", "manual", "setup and first use"),
    ("faq", "faq", "faq", "frequently asked questions"),
    ("troubleshooting", "troubleshooting", "troubleshoot", "troubleshooting"),
    ("error_codes", "error_codes", "errors", "error codes and indicators"),
    ("maintenance", "maintenance", "care", "maintenance and cleaning"),
    ("safety", "safety", "safety", "safety guidance"),
]


POLICY_DOCS = [
    {
        "doc_id": "policy-warranty-standard",
        "product_id": None,
        "kind": "policy",
        "title": "Standard warranty policy",
        "text": (
            "BrandAssist products carry a standard limited warranty against manufacturing defects in materials and "
            "workmanship. Most products are covered for 12 months from the purchase date; select products carry 24 "
            "months as noted on the product page. The warranty covers defects such as component failure under normal "
            "use. It does not cover accidental damage, misuse, unauthorized repair, normal wear, or consumable parts "
            "like filters. To make a claim, provide your order ID or proof of purchase; the support team will verify "
            "coverage, arrange repair or replacement, and may request photos. Keep your proof of purchase available."
        ),
    },
    {
        "doc_id": "policy-returns-standard",
        "product_id": None,
        "kind": "policy",
        "title": "Returns and refunds policy",
        "text": (
            "Items may be returned within 30 days of delivery for a refund or exchange. Unopened items in original "
            "packaging qualify for a full refund. Opened items that are in resalable condition may be accepted, "
            "though a restocking fee can apply for certain categories. To start a return, have your order ID and "
            "proof of purchase ready; the support team will issue a return authorization and instructions. Refunds "
            "are processed to the original payment method after the item is received and inspected. Hygiene-sensitive "
            "or consumable items may be non-returnable once opened."
        ),
    },
]


def _family_for(product_id: str) -> str | None:
    matches = [base for base in FAMILIES if product_id == base or product_id.startswith(base + "-")]
    if not matches:
        return None
    return max(matches, key=len)


def build_documents(products: list[tuple[str, str]]) -> list[dict]:
    docs: list[dict] = list(POLICY_DOCS)
    today = date.today().isoformat()
    for product_id, name in products:
        family = _family_for(product_id)
        if not family:
            continue
        content = FAMILIES[family]
        for section_key, kind, prefix, title_suffix in SECTIONS:
            docs.append(
                {
                    "doc_id": f"{prefix}-{product_id}",
                    "product_id": product_id,
                    "kind": kind,
                    "title": f"{name} {title_suffix}",
                    "text": content[section_key].format(name=name),
                }
            )
    return docs


def write_db(db_path: Path, docs: list[dict]) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("DELETE FROM knowledge_documents;")
        today = date.today().isoformat()
        conn.executemany(
            "INSERT INTO knowledge_documents (doc_id, product_id, kind, title, text, source_url, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                (d["doc_id"], d["product_id"], d["kind"], d["title"], d["text"], "synthetic://brandassist", today)
                for d in docs
            ],
        )
        conn.commit()


def write_json(json_path: Path, docs: list[dict]) -> None:
    payload = [
        {"id": d["doc_id"], "product_id": d["product_id"], "kind": d["kind"], "title": d["title"], "text": d["text"]}
        for d in docs
    ]
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate rich original knowledge base for BrandAssist.")
    parser.add_argument("--db-path", default="data/brandassist.db")
    parser.add_argument("--json-path", default="data/brand/knowledge_base.json")
    args = parser.parse_args()

    db_path = Path(args.db_path)
    with sqlite3.connect(db_path) as conn:
        products = conn.execute("SELECT product_id, name FROM products ORDER BY product_id").fetchall()

    docs = build_documents([(row[0], row[1]) for row in products])
    write_db(db_path, docs)
    write_json(Path(args.json_path), docs)

    by_kind: dict[str, int] = {}
    for d in docs:
        by_kind[d["kind"]] = by_kind.get(d["kind"], 0) + 1
    print(f"Wrote {len(docs)} knowledge documents across {len(products)} products.")
    print("By kind:", json.dumps(by_kind, indent=2))


if __name__ == "__main__":
    main()
