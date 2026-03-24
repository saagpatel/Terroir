import Foundation

actor EnrichmentService {
    private var cache: [Int: EnrichmentData] = [:]

    /// Bundled mock enrichment data for well-known locations.
    private let mockData: [Int: EnrichmentData] = {
        var data: [Int: EnrichmentData] = [:]

        // Burgundy, France (~47.2°N, 5.0°E) → latBand=274, lonBand=370 → index=274*720+370=197650
        data[197_650] = EnrichmentData(
            soilDescription: "Kimmeridgian clay-limestone over Jurassic bedrock. Thin topsoil rich in iron oxide, "
                + "with fossil oyster shells visible in exposed cuts — the ancient seabed that gives Chablis its minerality.",
            climateDescription: "Continental with oceanic influence. Cold winters (-2°C January mean), warm summers (25°C July peak). "
                + "Late spring frosts remain the primary viticultural hazard.",
            vegetationDescription: "Pinot Noir and Chardonnay dominate, with remnant Burgundian oak forest on upper slopes. "
                + "NDVI indicates vigorous canopy from June through veraison.",
            geologicalHistory: "The Saône graben formed during Oligocene rifting, exposing a staircase of Jurassic limestone "
                + "that now defines the Côte d'Or escarpment.",
            nearbyAppellations: "Gevrey-Chambertin, Morey-Saint-Denis, Chambolle-Musigny, Vougeot, Vosne-Romanée",
            culturalContext: "Cistercian monks at Clos de Vougeot systematically mapped soil differences in the 12th century, "
                + "creating the concept of 'climat' — individual named plots defined by terroir."
        )

        // Marlborough, NZ (~-41.5°S, 173.9°E) → latBand=97, lonBand=707 → index=97*720+707=70547
        data[70_547] = EnrichmentData(
            soilDescription: "Young alluvial gravels over greywacke bedrock in the Wairau Valley. Free-draining, low fertility soils "
                + "stress vines productively, concentrating Sauvignon Blanc's signature aromatics.",
            climateDescription: "Maritime with high sunshine hours (2,409 annual average). Cool nights preserve acidity while warm days "
                + "drive flavour ripeness — the widest diurnal range in New Zealand wine country.",
            vegetationDescription: "Dominant Sauvignon Blanc canopy with increasing Pinot Noir on clay subsoils. "
                + "Native bush remnants (mānuka, kānuka) on surrounding hills.",
            geologicalHistory: nil,
            nearbyAppellations: "Wairau Valley, Southern Valleys, Awatere Valley",
            culturalContext: "Montana (now Brancott Estate) planted the first Sauvignon Blanc here in 1973. "
                + "The 1985 Cloudy Bay vintage put Marlborough on the global wine map."
        )

        // Napa Valley, CA (~38.5°N, -122.3°W) → latBand=257, lonBand=115 → index=257*720+115=185155
        data[185_155] = EnrichmentData(
            soilDescription: "Over 100 soil series in a 30-mile valley. Volcanic ash on benchlands (Oakville, Rutherford), "
                + "alluvial fans on the valley floor, with residual volcanic soils on Spring and Howell Mountain.",
            climateDescription: "Mediterranean with pronounced fog influence from San Pablo Bay. "
                + "Summer highs reach 35°C on the valley floor but the fog line keeps Carneros 10°C cooler.",
            vegetationDescription: "Cabernet Sauvignon dominates benchland plantings. Valley floor shows mixed Merlot and Chardonnay. "
                + "Douglas fir and coast live oak on the Mayacamas and Vaca ranges.",
            geologicalHistory: "The valley sits at the junction of the Pacific and North American plates. "
                + "Volcanic activity from Mt. St. Helena deposited ash soils across the upper valley.",
            nearbyAppellations: "Oakville, Rutherford, Stags Leap District, Howell Mountain, Spring Mountain",
            culturalContext: "The 1976 Judgment of Paris — when Stag's Leap and Chateau Montelena defeated French grand crus — "
                + "transformed Napa from provincial curiosity to global benchmark."
        )

        // Barossa Valley, Australia (~-34.6°S, 138.9°E) → latBand=110, lonBand=637 → index=110*720+637=79837
        data[79_837] = EnrichmentData(
            soilDescription: "Red-brown earths and terra rossa over calcrete. Ancient pre-Cambrian geology gives Barossa "
                + "some of the oldest soils in any wine region on Earth.",
            climateDescription: "Warm Mediterranean with low rainfall (500mm annual). Hot summers tempered by cooling "
                + "afternoon breezes from Gulf St Vincent.",
            vegetationDescription: nil,
            geologicalHistory: nil,
            nearbyAppellations: "Eden Valley, Clare Valley, McLaren Vale, Adelaide Hills",
            culturalContext: "Silesian Lutheran settlers planted vines in the 1840s. Some Barossa Shiraz vines are 170+ years old — "
                + "pre-phylloxera, ungrafted, among the oldest producing vines in the world."
        )

        // Mid-Atlantic Ocean (~30°N, -40°W) → ocean cell
        // latBand=240, lonBand=280 → index=240*720+280=173080
        data[173_080] = EnrichmentData(
            soilDescription: nil,
            climateDescription: "Open Atlantic, subtropical high pressure zone. Sea surface temperatures 22-26°C. "
                + "The Sargasso Sea's calm, warm waters host unique pelagic ecosystems.",
            vegetationDescription: nil,
            geologicalHistory: "The Mid-Atlantic Ridge — Earth's longest mountain range — runs directly beneath these waters, "
                + "marking the boundary where the African and American plates drift apart at 2.5cm per year.",
            nearbyAppellations: nil,
            culturalContext: nil
        )

        return data
    }()

    func fetch(for coordinate: GeoCoordinate) async -> EnrichmentData? {
        let index = coordinate.gridCellIndex

        // Check cache first
        if let cached = cache[index] {
            return cached
        }

        // Check bundled mock data
        if let mock = mockData[index] {
            cache[index] = mock
            return mock
        }

        // In production, this would call CloudKit Functions or Vercel Edge Functions.
        // For v1, we return nil for locations without bundled data.
        // The 5s timeout and network call will be added when the enrichment backend is built.
        return nil
    }

    func clearCache() {
        cache.removeAll()
    }
}
