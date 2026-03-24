import SceneKit
import SwiftUI

struct GlobeView: UIViewRepresentable {
    let globeScene: GlobeScene
    var onTap: ((GeoCoordinate) -> Void)?

    func makeUIView(context: Context) -> SCNView {
        let scnView = SCNView()
        scnView.scene = globeScene.makeScene()
        scnView.backgroundColor = .black
        scnView.antialiasingMode = .multisampling4X
        scnView.allowsCameraControl = false
        scnView.showsStatistics = false

        let panGesture = UIPanGestureRecognizer(
            target: context.coordinator,
            action: #selector(Coordinator.handlePan(_:))
        )
        scnView.addGestureRecognizer(panGesture)

        let tapGesture = UITapGestureRecognizer(
            target: context.coordinator,
            action: #selector(Coordinator.handleTap(_:))
        )
        scnView.addGestureRecognizer(tapGesture)

        let pinchGesture = UIPinchGestureRecognizer(
            target: context.coordinator,
            action: #selector(Coordinator.handlePinch(_:))
        )
        scnView.addGestureRecognizer(pinchGesture)

        context.coordinator.scnView = scnView

        return scnView
    }

    func updateUIView(_: SCNView, context _: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(globeScene: globeScene, onTap: onTap)
    }

    final class Coordinator: NSObject {
        let globeScene: GlobeScene
        var onTap: ((GeoCoordinate) -> Void)?
        weak var scnView: SCNView?

        private var previousPanPoint: CGPoint = .zero
        private var isRotating = false

        init(globeScene: GlobeScene, onTap: ((GeoCoordinate) -> Void)?) {
            self.globeScene = globeScene
            self.onTap = onTap
        }

        @objc func handlePan(_ gesture: UIPanGestureRecognizer) {
            guard let view = scnView else { return }

            let translation = gesture.translation(in: view)

            switch gesture.state {
            case .began:
                previousPanPoint = .zero
                globeScene.pauseAutoRotation()
                isRotating = true

            case .changed:
                let dx = Float(translation.x - previousPanPoint.x)
                let dy = Float(translation.y - previousPanPoint.y)
                previousPanPoint = translation

                let sensitivity: Float = 0.005
                let orbit = globeScene.cameraOrbitNode

                // Horizontal pan rotates around Y axis
                orbit.eulerAngles.y -= dx * sensitivity
                // Vertical pan rotates around X axis, clamped to avoid flipping
                let newX = orbit.eulerAngles.x - dy * sensitivity
                orbit.eulerAngles.x = max(-.pi / 2 + 0.1, min(.pi / 2 - 0.1, newX))

            case .ended, .cancelled:
                isRotating = false
                // Delay before resuming auto-rotation
                DispatchQueue.main.asyncAfter(deadline: .now() + 3.0) { [weak self] in
                    guard let self, !self.isRotating else { return }
                    self.globeScene.resumeAutoRotation()
                }

            default:
                break
            }
        }

        @objc func handleTap(_ gesture: UITapGestureRecognizer) {
            guard let view = scnView else { return }

            let location = gesture.location(in: view)
            let hitResults = view.hitTest(location, options: [
                .searchMode: SCNHitTestSearchMode.closest.rawValue,
            ])

            guard let hit = hitResults.first else {
                return
            }

            let localPoint = hit.localCoordinates
            let coordinate = scenePointToGeoCoordinate(localPoint)
            onTap?(coordinate)
        }

        @objc func handlePinch(_ gesture: UIPinchGestureRecognizer) {
            guard let cameraNode = globeScene.cameraOrbitNode.childNodes.first else { return }

            switch gesture.state {
            case .changed:
                let currentZ = cameraNode.position.z
                let newZ = currentZ / Float(gesture.scale)
                cameraNode.position.z = max(1.5, min(5.0, newZ))
                gesture.scale = 1.0

            default:
                break
            }
        }

        /// Converts a SceneKit local hit point on a unit sphere to lat/lon.
        private func scenePointToGeoCoordinate(_ point: SCNVector3) -> GeoCoordinate {
            // On a unit sphere: x = cos(lat)*sin(lon), y = sin(lat), z = cos(lat)*cos(lon)
            let latitude = Double(asin(point.y)) * 180.0 / .pi
            let longitude = Double(atan2(point.x, point.z)) * 180.0 / .pi

            return GeoCoordinate(
                latitude: max(-90, min(90, latitude)),
                longitude: max(-180, min(180, longitude))
            )
        }
    }
}
