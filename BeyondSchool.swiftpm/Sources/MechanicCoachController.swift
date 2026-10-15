import Foundation
@preconcurrency import AVFoundation
import simd

#if canImport(RealityKit)
import RealityKit
#endif

@MainActor
public final class MechanicCoachController: NSObject, AVSpeechSynthesizerDelegate {
    public private(set) var isPresent = false
    public private(set) var beaconPulse: Float = 0
    public private(set) var gesturePhase: Float = 0
    public private(set) var speechEnabled = true
    public private(set) var activeSubtitle = ""
    public private(set) var speechFinishedCount = 0
    private let synthesizer = AVSpeechSynthesizer()

    public override init() {
        super.init()
        synthesizer.delegate = self
    }

    public func setPresent(_ present: Bool) {
        isPresent = present
    }

    public func setSpeechEnabled(_ enabled: Bool) {
        speechEnabled = enabled
        if !enabled { synthesizer.stopSpeaking(at: .immediate) }
    }

    public func speak(_ text: String) {
        guard speechEnabled else { return }
        let utterance = AVSpeechUtterance(string: text)
        activeSubtitle = text
        utterance.rate = 0.48
        utterance.voice = AVSpeechSynthesisVoice(language: "en-IN")
            ?? AVSpeechSynthesisVoice(language: "en-US")
        synthesizer.speak(utterance)
    }

    nonisolated public func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didFinish utterance: AVSpeechUtterance) {
        Task { @MainActor [weak self] in
            self?.activeSubtitle = ""
            self?.speechFinishedCount += 1
        }
    }

    nonisolated public func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didCancel utterance: AVSpeechUtterance) {
        Task { @MainActor [weak self] in
            self?.activeSubtitle = ""
        }
    }

    public func update(deltaTime: Float) {
        guard deltaTime > 0 else { return }
        gesturePhase += deltaTime
        beaconPulse = 0.5 + 0.5 * sin(gesturePhase * 4)
    }

    #if canImport(RealityKit)
    public func install(in root: Entity, roadHeight: Float, wheelCenter: SIMD3<Float>) {
        guard !isPresent else { return }
        let mentor = Entity()
        mentor.name = "MechanicMentor_Root"
        mentor.position = [wheelCenter.x - 0.80, roadHeight + 0.31, wheelCenter.z + 0.80]

        let vest = ModelEntity(
            mesh: .generateBox(size: [0.38, 0.22, 0.62]),
            materials: [SimpleMaterial(color: .orange, isMetallic: false)]
        )
        vest.name = "MechanicMentor_HighVisibilityVest"
        mentor.addChild(vest)

        let head = ModelEntity(
            mesh: .generateSphere(radius: 0.14),
            materials: [SimpleMaterial(color: .brown, isMetallic: false)]
        )
        head.position = [0, 0, 0.45]
        mentor.addChild(head)

        let hat = ModelEntity(
            mesh: .generateCylinder(height: 0.08, radius: 0.17),
            materials: [SimpleMaterial(color: .yellow, isMetallic: false)]
        )
        hat.position = [0, 0, 0.57]
        mentor.addChild(hat)

        for x in [-0.13, 0.13] {
            let strip = ModelEntity(
                mesh: .generateBox(size: [0.035, 0.23, 0.58]),
                materials: [UnlitMaterial(color: .white)]
            )
            strip.transform.translation = SIMD3<Float>(Float(x), -0.12, 0)
            mentor.addChild(strip)
        }

        let arm = ModelEntity(
            mesh: .generateBox(size: [0.10, 0.10, 0.42]),
            materials: [SimpleMaterial(color: .orange, isMetallic: false)]
        )
        arm.name = "MechanicMentor_GesturingArm"
        arm.position = [0.28, 0, 0.12]
        mentor.addChild(arm)

        let beacon = ModelEntity(
            mesh: .generateCylinder(height: 0.12, radius: 0.16),
            materials: [UnlitMaterial(color: .orange)]
        )
        beacon.name = "ServiceVanBeacon"
        beacon.position = [0, 0.45, 0]
        mentor.addChild(beacon)
        beacon.components.set(PointLightComponent(intensity: 500, attenuationRadius: 2.5))
        root.addChild(mentor)
        isPresent = true
    }

    public func synchronize(in root: Entity, deltaTime: Float) {
        update(deltaTime: deltaTime)
        guard let mentor = root.findEntity(named: "MechanicMentor_Root") else { return }
        mentor.isEnabled = isPresent
        let breathing = 1 + 0.015 * sin(gesturePhase * 1.8)
        mentor.scale = [breathing, breathing, breathing]
        mentor.findEntity(named: "MechanicMentor_GesturingArm")?.transform.rotation =
            simd_quatf(angle: sin(gesturePhase * 2.2) * 0.22, axis: [0, 1, 0])
        if let head = mentor.findEntity(named: "MechanicMentor_HighVisibilityVest") {
            let toWheel = SIMD3<Float>(-0.6, 0, 0.8)
            head.orientation = simd_quatf(from: [0, 0, 1], to: simd_normalize(toWheel))
        }
        mentor.findEntity(named: "ServiceVanBeacon")?.scale = [1, 1, 0.92 + beaconPulse * 0.22]
    }
    #endif
}

#if canImport(RealityKit)
private extension Entity {
    func findEntity(named name: String) -> Entity? {
        if self.name == name { return self }
        for child in children {
            if let match = child.findEntity(named: name) { return match }
        }
        return nil
    }
}
#endif
