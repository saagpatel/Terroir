import Foundation

enum TemplateEngine {
    // MARK: - Opening Templates (3 per dimension)

    private static let openings: [FlavorDimension: [String]] = [
        .earthy: [
            "The ground here speaks in deep, loamy tones — a rich bassline of turned soil and wet clay after rain.",
            "Root cellars and forest floors define this landscape, where every handful of earth carries the weight of centuries.",
            "There is something primal underfoot: the dense, mushroom-dark earthiness of land that has been worked and reworked.",
        ],
        .mineral: [
            "Stone and slate announce themselves with crystalline clarity, as if the bedrock itself were singing.",
            "A vein of mineral tension runs through this place — chalk dust, wet flint, the cold spark of granite on steel.",
            "The minerality here is austere and beautiful, recalling limestone caves and rain hitting ancient rock faces.",
        ],
        .bright: [
            "Light pours through this profile like morning sun through cathedral glass — vivid, lifting, electric.",
            "There is a luminous acidity here that sharpens every other note, a bright wire of tension running through the landscape.",
            "Brightness defines this terroir: crisp, clean, almost blinding in its intensity, like biting into a cold apple at altitude.",
        ],
        .citric: [
            "Citrus groves seem to hang in the air — Meyer lemon zest, blood orange pith, the oils of bergamot at dusk.",
            "A sharp citric thread weaves through the profile, all grapefruit rind and lime leaf, tart and relentless.",
            "The citrus character here is sun-drenched and generous, recalling marmalade made from fruit still warm off the tree.",
        ],
        .floral: [
            "Petals and pollen drift across this profile — jasmine at twilight, dried lavender crushed between fingers.",
            "A garden in full riot: rose water, orange blossom, the honeyed sweetness of elderflower on a still afternoon.",
            "The floral dimension is delicate but persistent, like the scent of wildflowers caught on a hillside breeze.",
        ],
        .herbaceous: [
            "Crush a leaf between your fingers and you have this terroir — tarragon, thyme, the green snap of fresh basil.",
            "The herbal character is vivid and slightly wild: rosemary hedges along a coastal path, sage after summer rain.",
            "A green, aromatic herbaceousness dominates, recalling kitchen gardens and the sharp freshness of just-cut herbs.",
        ],
        .smoky: [
            "Woodsmoke and char define this landscape — campfires at elevation, volcanic soil still warm underfoot.",
            "There is a dark, smoldering quality here: spent hearths, charred oak, the aftermath of a controlled burn.",
            "Smoke hangs in the profile like morning mist in a valley — subtle, persistent, and deeply atmospheric.",
        ],
        .woody: [
            "Oak and cedar frame this terroir in warm, structural tones — barrel staves, sandalwood, pencil shavings.",
            "The woody character is venerable and deep: old-growth forest floors, the vanilla sweetness of toasted barrels.",
            "Dense and architectural, the wood notes here suggest centuries of growth — tannin-rich bark and resinous heartwood.",
        ],
        .saline: [
            "Salt spray and sea air cut through the profile — brine-kissed rocks, oyster shells, the tang of open water.",
            "A maritime salinity pervades, recalling fishing villages, kelp beds, and the mineral edge of coastal winds.",
            "The ocean is never far: saline notes wash through like a retreating tide, leaving mineral traces on warm stone.",
        ],
        .tannic: [
            "Structure and grip define this place — the drying astringency of walnut skins, black tea steeped too long.",
            "Tannin provides the architecture: muscular, unyielding, the kind of grip that demands patience and rewards it.",
            "There is a noble austerity here, all persimmon skin and pomegranate tannin, building toward something profound.",
        ],
        .vegetal: [
            "Green and alive: bell pepper, snap peas, the almost-bitter freshness of raw asparagus in early spring.",
            "The vegetal character is honest and direct — leafy greens, artichoke hearts, the chlorophyll tang of new growth.",
            "Something green and vital pulses through this terroir, like walking through a market garden at dawn.",
        ],
        .aromatic: [
            "Spice and perfume fill the air — cinnamon bark, star anise, the warm complexity of a well-stocked apothecary.",
            "An aromatic tapestry unfolds: cardamom, clove, saffron threads, the exotic warmth of faraway trade routes.",
            "The aromatics here are layered and intoxicating — incense resin, dried flowers, the deep sweetness of vanilla bean.",
        ],
    ]

    // MARK: - Modifier Clauses

    private static func modifierClause(for notes: [(FlavorDimension, Float)]) -> String {
        guard notes.count >= 2 else { return "" }

        let secondary = notes[1]
        let intensity = secondary.1

        if intensity > 0.7 {
            return " Alongside, a powerful \(secondary.0.displayLabel.lowercased()) presence insists on attention,"
                + " adding complexity and depth to the overall character."
        } else if intensity > 0.5 {
            return " Beneath the surface, \(secondary.0.displayLabel.lowercased()) undertones provide"
                + " a complementary counterpoint, enriching the profile with quiet nuance."
        } else {
            return " A whisper of \(secondary.0.displayLabel.lowercased()) hides in the margins,"
                + " barely perceptible but essential to the whole."
        }
    }

    // MARK: - Elevation Context

    private static func elevationContext(_ band: Int) -> String {
        switch band {
        case 0:
            " At this low elevation, warmth and humidity compress the flavor palette into something dense and immediate."
        case 1:
            " Moderate elevation lends a refreshing clarity, as cooler nights preserve acidity and extend the aromatic range."
        case 2:
            " High altitude sharpens everything here — thinner air, wider temperature swings, a crystalline precision in every note."
        case 3:
            " At extreme elevation, the landscape is austere and wind-scoured, producing flavors of remarkable concentration and purity."
        default:
            ""
        }
    }

    // MARK: - Ocean Description

    private static func oceanDescription(zone: Int) -> String {
        let oceanZone = OceanZone(rawValue: zone) ?? .temperate

        switch oceanZone {
        case .polar:
            return "These polar waters carry a crystalline mineral intensity — cold, bracing, "
                + "with the sharp salinity of ancient ice shelves dissolving into dark currents. "
                + "Imagine biting into a frozen oyster: brine, steel, and the vast silence of glacial seas."
        case .temperate:
            return "The temperate sea speaks in balanced tones — kelp beds and barnacled pilings, "
                + "the honest salt of working harbors. There is warmth beneath the brine, "
                + "a maritime generosity that softens the mineral edge."
        case .tropical:
            return "Warm tropical waters pulse with salinity and a surprising floral sweetness — "
                + "coral reefs and sun-heated shallows, coconut husks floating in turquoise brine. "
                + "The ocean here is generous, almost perfumed."
        }
    }

    // MARK: - Public API

    static func describe(
        vector: FlavorVector,
        isOcean: Bool,
        oceanZone: Int = 0,
        elevationBand: Int = 0
    ) -> String {
        if isOcean {
            return oceanDescription(zone: oceanZone)
        }

        let notes = vector.dominantNotes(threshold: 0.30, maxCount: 5)

        guard let primary = notes.first else {
            return "This location yields a subtle, understated profile — "
                + "no single dimension dominates, suggesting a gentle equilibrium across the flavor spectrum."
        }

        let dimension = primary.0
        let templates = openings[dimension] ?? openings[.earthy]!
        let templateIndex = abs(Int(primary.1 * 1000)) % templates.count
        var prose = templates[templateIndex]

        prose += modifierClause(for: notes)

        if notes.count >= 3 {
            let tertiary = notes[2]
            prose += " Further still, traces of \(tertiary.0.displayLabel.lowercased())"
                + " round out the expression."
        }

        prose += elevationContext(elevationBand)

        return prose
    }
}
