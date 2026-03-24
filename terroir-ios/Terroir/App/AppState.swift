import Foundation
import SwiftUI

enum GlobeOverlay: String, CaseIterable, Sendable, Identifiable {
    case none = "None"
    case soil = "Soil"
    case climate = "Climate"
    case vegetation = "Vegetation"

    var id: String { rawValue }

    var imageName: String? {
        switch self {
        case .none: nil
        case .soil: "overlay_soil"
        case .climate: "overlay_climate"
        case .vegetation: "overlay_vegetation"
        }
    }

    var iconName: String {
        switch self {
        case .none: "globe"
        case .soil: "mountain.2"
        case .climate: "cloud.sun"
        case .vegetation: "leaf"
        }
    }
}

enum AppError: Error, LocalizedError, Sendable {
    case lookupFailed(String)
    case locationFailed(String)

    var errorDescription: String? {
        switch self {
        case .lookupFailed(let message): message
        case .locationFailed(let message): message
        }
    }
}

@Observable
@MainActor
final class AppState {
    // MARK: - Globe State

    var currentOverlay: GlobeOverlay = .none
    let globeScene = GlobeScene()

    // MARK: - Flavor Card State

    var showingCard = false
    var selectedCoordinate: GeoCoordinate?
    var selectedVector: FlavorVector?
    var selectedLocationName: String = ""
    var selectedIsOcean = false
    var selectedOceanZone = 0
    var selectedElevationBand = 0

    // MARK: - Enrichment State

    var showingDetail = false
    var enrichmentData: EnrichmentData?

    // MARK: - Share State

    var showingShare = false
    var shareImage: UIImage?

    // MARK: - Loading & Error

    var isLoading = false
    var errorMessage: String?
    var showingError = false

    // MARK: - Services

    let flavorLookup = FlavorLookup()
    let locationService = LocationService()
    let enrichmentService = EnrichmentService()

    // MARK: - Initialization

    func loadFlavorGrid() async {
        do {
            try await flavorLookup.load()
        } catch {
            errorMessage = "Failed to load flavor data: \(error.localizedDescription)"
            showingError = true
        }
    }

    // MARK: - Tap → Lookup → Show Card

    func handleGlobeTap(at coordinate: GeoCoordinate) async {
        isLoading = true
        errorMessage = nil

        do {
            let result = try await flavorLookup.lookup(coordinate: coordinate)
            let name = await locationService.reverseGeocode(coordinate)

            selectedCoordinate = coordinate
            selectedVector = result.vector
            selectedLocationName = name
            selectedIsOcean = result.isOcean
            selectedOceanZone = result.oceanZone
            selectedElevationBand = result.elevationBand

            withAnimation(.spring(response: 0.4, dampingFraction: 0.85)) {
                showingCard = true
            }
        } catch {
            errorMessage = error.localizedDescription
            showingError = true
        }

        isLoading = false
    }

    // MARK: - More Detail

    func fetchEnrichment() async {
        guard let coordinate = selectedCoordinate else { return }
        enrichmentData = await enrichmentService.fetch(for: coordinate)
        showingDetail = true
    }

    // MARK: - Share

    func prepareShareCard() {
        guard let vector = selectedVector, let coordinate = selectedCoordinate else { return }

        let shareView = ShareCardView(
            vector: vector,
            coordinate: coordinate,
            locationName: selectedLocationName,
            isOcean: selectedIsOcean,
            oceanZone: selectedOceanZone,
            elevationBand: selectedElevationBand
        )
        shareImage = shareView.renderImage()
        showingShare = shareImage != nil
    }

    // MARK: - Dismiss

    func dismissCard() {
        withAnimation(.spring(response: 0.35, dampingFraction: 0.85)) {
            showingCard = false
        }
        selectedCoordinate = nil
        selectedVector = nil
        enrichmentData = nil
    }

    // MARK: - Overlay

    func setOverlay(_ overlay: GlobeOverlay) {
        currentOverlay = overlay
        globeScene.setOverlay(overlay.imageName)
    }

    // MARK: - My Location

    func goToMyLocation() async {
        do {
            let coordinate = try await locationService.requestLocation()
            await handleGlobeTap(at: coordinate)
        } catch {
            errorMessage = error.localizedDescription
            showingError = true
        }
    }
}
