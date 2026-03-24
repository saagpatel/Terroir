import SceneKit
import Foundation

final class GlobeScene: @unchecked Sendable {
    let scene: SCNScene
    let sphereNode: SCNNode
    let cameraOrbitNode: SCNNode

    private let cameraNode: SCNNode

    init() {
        scene = SCNScene()
        sphereNode = SCNNode()
        cameraOrbitNode = SCNNode()
        cameraNode = SCNNode()
    }

    func makeScene() -> SCNScene {
        // Sphere geometry
        let sphere = SCNSphere(radius: 1.0)
        sphere.segmentCount = 96

        let material = SCNMaterial()
        if let texturePath = Bundle.main.path(forResource: "globe_base", ofType: "jpg") {
            material.diffuse.contents = UIImage(contentsOfFile: texturePath)
        }
        material.diffuse.wrapS = .clamp
        material.diffuse.wrapT = .clamp
        material.specular.contents = UIColor(white: 0.15, alpha: 1.0)
        material.shininess = 0.3
        material.lightingModel = .blinn
        sphere.materials = [material]

        sphereNode.geometry = sphere
        sphereNode.name = "globe"
        scene.rootNode.addChildNode(sphereNode)

        // Camera orbit (allows rotation via gestures)
        cameraNode.camera = SCNCamera()
        cameraNode.camera?.fieldOfView = 60
        cameraNode.camera?.zNear = 0.1
        cameraNode.camera?.zFar = 100
        cameraNode.position = SCNVector3(0, 0, 2.5)
        cameraNode.name = "camera"

        cameraOrbitNode.addChildNode(cameraNode)
        cameraOrbitNode.name = "cameraOrbit"
        scene.rootNode.addChildNode(cameraOrbitNode)

        // Ambient light
        let ambientLight = SCNNode()
        ambientLight.light = SCNLight()
        ambientLight.light?.type = .ambient
        ambientLight.light?.color = UIColor(white: 0.4, alpha: 1.0)
        ambientLight.light?.intensity = 600
        scene.rootNode.addChildNode(ambientLight)

        // Directional light (sun-like)
        let sunLight = SCNNode()
        sunLight.light = SCNLight()
        sunLight.light?.type = .directional
        sunLight.light?.color = UIColor(white: 0.95, alpha: 1.0)
        sunLight.light?.intensity = 800
        sunLight.position = SCNVector3(5, 5, 5)
        sunLight.look(at: SCNVector3Zero)
        scene.rootNode.addChildNode(sunLight)

        // Subtle auto-rotation
        let rotation = SCNAction.repeatForever(
            SCNAction.rotateBy(x: 0, y: CGFloat(0.05), z: 0, duration: 1.0)
        )
        sphereNode.runAction(rotation, forKey: "autoRotate")

        scene.background.contents = UIColor.black

        return scene
    }

    func setOverlay(_ imageName: String?) {
        guard let geometry = sphereNode.geometry as? SCNSphere else { return }
        guard let material = geometry.firstMaterial else { return }

        if let imageName,
           let path = Bundle.main.path(forResource: imageName, ofType: "png"),
           let image = UIImage(contentsOfFile: path) {
            let overlayMaterial = SCNMaterialProperty()
            overlayMaterial.contents = image
            material.transparent.contents = image
            material.transparent.wrapS = .clamp
            material.transparent.wrapT = .clamp
        } else {
            material.transparent.contents = nil
        }
    }

    func pauseAutoRotation() {
        sphereNode.removeAction(forKey: "autoRotate")
    }

    func resumeAutoRotation() {
        let rotation = SCNAction.repeatForever(
            SCNAction.rotateBy(x: 0, y: CGFloat(0.05), z: 0, duration: 1.0)
        )
        sphereNode.runAction(rotation, forKey: "autoRotate")
    }
}
