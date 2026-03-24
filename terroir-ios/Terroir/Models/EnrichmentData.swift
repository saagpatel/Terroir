import Foundation

struct EnrichmentData: Codable, Sendable, Equatable {
    var soilDescription: String?
    var climateDescription: String?
    var vegetationDescription: String?
    var geologicalHistory: String?
    var nearbyAppellations: String?
    var culturalContext: String?

    var hasContent: Bool {
        [soilDescription, climateDescription, vegetationDescription,
         geologicalHistory, nearbyAppellations, culturalContext]
            .contains { $0 != nil }
    }
}
