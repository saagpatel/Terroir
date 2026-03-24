import CoreLocation
import Foundation

enum LocationError: Error, LocalizedError {
    case permissionDenied
    case locationUnavailable
    case timeout

    var errorDescription: String? {
        switch self {
        case .permissionDenied:
            "Location access was denied. Enable it in Settings to use your current location."
        case .locationUnavailable:
            "Unable to determine your location. Try again in a moment."
        case .timeout:
            "Location request timed out. Please try again."
        }
    }
}

@Observable
@MainActor
final class LocationService: NSObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()
    private var continuation: CheckedContinuation<GeoCoordinate, Error>?
    private(set) var authorizationStatus: CLAuthorizationStatus = .notDetermined

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyKilometer
        authorizationStatus = manager.authorizationStatus
    }

    func requestLocation() async throws -> GeoCoordinate {
        try await withCheckedThrowingContinuation { continuation in
            self.continuation = continuation

            switch manager.authorizationStatus {
            case .notDetermined:
                manager.requestWhenInUseAuthorization()
            case .authorizedWhenInUse, .authorizedAlways:
                manager.requestLocation()
            case .denied, .restricted:
                self.continuation = nil
                continuation.resume(throwing: LocationError.permissionDenied)
            @unknown default:
                self.continuation = nil
                continuation.resume(throwing: LocationError.locationUnavailable)
            }
        }
    }

    nonisolated func locationManager(_: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.first else { return }

        let coordinate = GeoCoordinate(
            latitude: location.coordinate.latitude,
            longitude: location.coordinate.longitude
        )

        Task { @MainActor in
            continuation?.resume(returning: coordinate)
            continuation = nil
        }
    }

    nonisolated func locationManager(_: CLLocationManager, didFailWithError error: Error) {
        Task { @MainActor in
            continuation?.resume(throwing: LocationError.locationUnavailable)
            continuation = nil
        }
    }

    nonisolated func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        let status = manager.authorizationStatus

        Task { @MainActor in
            self.authorizationStatus = status

            if status == .authorizedWhenInUse || status == .authorizedAlways {
                if self.continuation != nil {
                    manager.requestLocation()
                }
            } else if status == .denied || status == .restricted {
                self.continuation?.resume(throwing: LocationError.permissionDenied)
                self.continuation = nil
            }
        }
    }

    /// Reverse geocode a coordinate into a human-readable place name.
    func reverseGeocode(_ coordinate: GeoCoordinate) async -> String {
        let geocoder = CLGeocoder()
        let location = CLLocation(latitude: coordinate.latitude, longitude: coordinate.longitude)

        do {
            let placemarks = try await geocoder.reverseGeocodeLocation(location)
            if let placemark = placemarks.first {
                let components = [placemark.locality, placemark.administrativeArea, placemark.country]
                let name = components.compactMap { $0 }.joined(separator: ", ")
                return name.isEmpty ? coordinate.displayString : name
            }
        } catch {
            // Silently fall back to coordinate display
        }

        return coordinate.displayString
    }
}
