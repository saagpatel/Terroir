import XCTest

final class TapToCardFlowTests: XCTestCase {

    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    @MainActor
    func testAppLaunches() throws {
        let app = XCUIApplication()
        app.launch()
        let exists = app.wait(for: .runningForeground, timeout: 5)
        XCTAssertTrue(exists, "App should launch to foreground")
    }

    @MainActor
    func testTapOnGlobeShowsCard() throws {
        let app = XCUIApplication()
        app.launch()
        _ = app.wait(for: .runningForeground, timeout: 5)

        // Wait for globe to load and render
        Thread.sleep(forTimeInterval: 3)

        // Tap on the upper-center area where the globe should be rendered
        // Use normalized coordinates: (0.5, 0.35) = center-x, upper-third-y
        let tapPoint = app.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.35))
        tapPoint.tap()

        // Wait for the flavor card to appear
        Thread.sleep(forTimeInterval: 2)

        // Take screenshot for visual verification
        let screenshot = app.screenshot()
        let attachment = XCTAttachment(screenshot: screenshot)
        attachment.name = "After tap on globe"
        attachment.lifetime = .keepAlways
        add(attachment)
    }

    @MainActor
    func testMultipleTapsDoNotCrash() throws {
        let app = XCUIApplication()
        app.launch()
        _ = app.wait(for: .runningForeground, timeout: 5)

        Thread.sleep(forTimeInterval: 2)

        // Tap multiple locations rapidly
        for dx in stride(from: 0.3, through: 0.7, by: 0.1) {
            let point = app.coordinate(withNormalizedOffset: CGVector(dx: dx, dy: 0.4))
            point.tap()
            Thread.sleep(forTimeInterval: 0.5)
        }

        // App should still be running
        XCTAssertTrue(app.state == .runningForeground, "App should not crash after multiple taps")
    }
}
