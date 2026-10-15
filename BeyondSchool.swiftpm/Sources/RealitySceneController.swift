import Foundation
import simd

#if canImport(RealityKit)
import RealityKit
import SwiftUI

@MainActor
public final class RealitySceneController: ObservableObject {
    public struct WorldBoundsRecord: Sendable, Equatable {
        public var min: SIMD3<Float>
        public var max: SIMD3<Float>

        public var center: SIMD3<Float> { (min + max) * 0.5 }
        public var height: Float { max.y - min.y }

        public init(min: SIMD3<Float>, max: SIMD3<Float>) {
            self.min = min
            self.max = max
        }
    }

    public struct WorldBoundsAudit: Sendable, Equatable {
        public var wheel: WorldBoundsRecord
        public var mirror: WorldBoundsRecord
        public var road: WorldBoundsRecord
        public var trafficLaneZ: Float
        public var roadHeight: Float
        public var mechanicFeetHeight: Float

        public init(
            wheel: WorldBoundsRecord,
            mirror: WorldBoundsRecord,
            road: WorldBoundsRecord,
            trafficLaneZ: Float,
            roadHeight: Float,
            mechanicFeetHeight: Float
        ) {
            self.wheel = wheel
            self.mirror = mirror
            self.road = road
            self.trafficLaneZ = trafficLaneZ
            self.roadHeight = roadHeight
            self.mechanicFeetHeight = mechanicFeetHeight
        }
    }

    @Published public private(set) var root: Entity?
    @Published public private(set) var isLoaded = false
    @Published public private(set) var validationIssues: [String] = []
    @Published public private(set) var worldBoundsAudit: WorldBoundsAudit?
    public let kinematics = MechanicalKinematics()
    public let audioEngine = SpatialAudioEngine()
    public let trafficController = TrafficCorridorController()
    public let mechanicController = MechanicCoachController()
    public private(set) var nightRecallEnabled = false
    public private(set) var lastKinematicUpdateTime: TimeInterval = 0
    public private(set) var lastInteractionFeedback = ""
    private var frameSubscription: Any?

    public static let interactiveNames = [
        "BTN_HazardSwitch_Pivot", "CONSOLE_GearSelector_Pivot", "CTRL_ParkingBrake_Pivot",
        "MIRROR_Driver", "DOOR_DriverRight_Pivot", "TRUNK_Lid_Pivot", "WHEEL_RL_FlatTarget",
        "JACK_Point_RL", "WHEEL_Spare_Pivot", "TOOL_ScissorJack_Root",
        "TOOL_LugWrench_Root", "TOOL_WarningTriangle_Root"
    ] + (0..<5).map { String(format: "LUG_RL_Nut_%02d_Pivot", $0) }

    public init() {}

    public func startFrameUpdates(in scene: RealityKit.Scene) {
        frameSubscription = scene.subscribe(to: SceneEvents.Update.self) { [weak self] event in
            Task { @MainActor in
                self?.update(deltaTime: Float(event.deltaTime))
            }
        }
    }

    public func stopFrameUpdates() {
        frameSubscription = nil
    }

    public func update(deltaTime: Float) {
        guard let root else { return }
        kinematics.step(deltaTime: deltaTime)
        trafficController.synchronize(in: root, deltaTime: deltaTime)
        if let audit = worldBoundsAudit {
            for vehicle in trafficController.vehicles {
                root.findEntity(named: "ContactShadow_\(vehicle.identifier)")?.position = [
                    vehicle.x,
                    audit.roadHeight + 0.008,
                    audit.trafficLaneZ
                ]
            }
        }
        mechanicController.synchronize(in: root, deltaTime: deltaTime)
        if trafficController.lastWakeImpulse != 0 {
            kinematics.injectWakeImpulse(direction: trafficController.lastWakeImpulse)
            attachAudioCue(.trafficWhoosh, to: "MIRROR_Driver")
            audioEngine.trigger(.trafficWhoosh, intensity: 1.0)
        }
        lastKinematicUpdateTime += TimeInterval(deltaTime)
        applyKinematics(to: root)
    }

    public func setFlatTyreState(_ enabled: Bool) {
        kinematics.setFlatTyreSag(enabled)
        if enabled {
            attachAudioCue(.flatTyreThump, to: "WHEEL_RL_FlatTarget")
            audioEngine.trigger(.flatTyreThump, intensity: 0.8)
        } else {
            audioEngine.stop(.flatTyreThump)
        }
    }

    public func setJackLift(progress: Float) {
        kinematics.setJackProgress(progress)
        if progress > 0, progress < 1 {
            attachAudioCue(.jackClick, to: "TOOL_ScissorJack_Root")
            audioEngine.trigger(.jackClick, intensity: progress)
        }
    }

    public func turnLug(_ index: Int, progress: Float, removed: Bool = false) {
        guard kinematics.lugStarOrder.contains(index) else { return }
        kinematics.turnLug(index, progress: progress, removed: removed)
        attachAudioCue(.wrenchCreak, to: "TOOL_LugWrench_Root")
        audioEngine.trigger(.wrenchCreak, intensity: max(0.2, progress))
    }

    public func pullFlatWheel(progress: Float) {
        kinematics.setFlatWheelPull(progress)
    }

    public func swapSpare(progress: Float) {
        kinematics.setSpareSwap(progress)
    }

    public func applyDrag(to name: String, translation: SIMD3<Float>, rotation: simd_quatf? = nil) {
        guard Self.interactiveNames.contains(name) || name == "TOOL_LugWrench_Root" || name == "TOOL_ScissorJack_Root" else { return }
        guard let object = entity(named: name) else { return }
        object.position += translation
        if let rotation {
            object.orientation = simd_slerp(object.orientation, rotation, 0.22)
        }
    }

    public func resolveInteractiveName(from entity: Entity) -> String? {
        var current: Entity? = entity
        while let candidate = current {
            if Self.interactiveNames.contains(candidate.name) {
                return candidate.name
            }
            current = candidate.parent
        }
        return nil
    }

    @discardableResult
    public func tapEntity(named name: String, model: RoadsideTrainerModel) -> Bool {
        guard Self.interactiveNames.contains(name) else { return false }
        model.setTrafficDangerZoneOccupied(trafficController.isDangerZoneOccupied)
        if let lugIndex = lugIndex(from: name), model.state == .assistedWheelChange {
            let expected = RoadsideTrainerModel.starPattern[safe: model.crackedLugs.count]
            guard expected == lugIndex else {
                lastInteractionFeedback = "Use the five-point star order to distribute clamp load and prevent brake-rotor warping."
                return false
            }
            return model.send(.crackLug(lugIndex))
        }
        if name == "DOOR_DriverRight_Pivot" {
            return model.send(.openDriverDoor)
        }
        lastInteractionFeedback = "Selected \(name.replacingOccurrences(of: "_", with: " "))."
        return true
    }

    public func setNightRecallMode(_ enabled: Bool) {
        nightRecallEnabled = enabled
        guard let root else { return }
        let headlamps = ["LAMP_Headlight_L", "LAMP_Headlight_R"]
        for name in headlamps {
            entity(named: name)?.components.set(
                SpotLightComponent(intensity: enabled ? 18_000 : 0, innerAngleInDegrees: 12, outerAngleInDegrees: 28, attenuationRadius: 18)
            )
        }
        let hazards = ["LAMP_Hazard_FL", "LAMP_Hazard_FR", "LAMP_Hazard_RL", "LAMP_Hazard_RR", "LAMP_Hazard_Side_R", "LAMP_Hazard_Side_L"]
        for name in hazards {
            entity(named: name)?.components.set(
                PointLightComponent(intensity: enabled ? 1_200 : 0, attenuationRadius: 3)
            )
        }
        if enabled {
            for name in ["LAMP_Hazard_FL", "LAMP_Hazard_FR", "LAMP_Hazard_RL", "LAMP_Hazard_RR"] {
                entity(named: name)?.components.set(
                    PointLightComponent(intensity: 280, attenuationRadius: 1.8)
                )
            }
            root.components.set(SceneLightingModeComponent(isNight: true))
        }
        if enabled {
            attachAudioCue(.trafficWhoosh, to: "MIRROR_Driver")
            audioEngine.trigger(.trafficWhoosh, intensity: 0.7)
        } else {
            audioEngine.stop(.trafficWhoosh)
        }
        root.components.set(SceneLightingModeComponent(isNight: enabled))
    }

    public func attachNightFlashlight(to camera: Entity, enabled: Bool) {
        camera.components.set(
            SpotLightComponent(
                intensity: enabled ? 2_400 : 0,
                innerAngleInDegrees: 18,
                outerAngleInDegrees: 34,
                attenuationRadius: 5
            )
        )
    }

    public func synchronize(with state: RoadsideTrainerModel.State) {
        setNightRecallMode(state == .recallChallenge)
        setFlatTyreState(state == .tyreWarningPullOver || state == .assistedWheelChange)
        mechanicController.setPresent(state == .trunkToolkitHandOff || state == .assistedWheelChange)
    }

    public func coupleWrench(to lugIndex: Int, progress: Float, removed: Bool = false) {
        guard let wrench = entity(named: "TOOL_LugWrench_Root"),
              let lug = entity(named: String(format: "LUG_RL_Nut_%02d_Pivot", lugIndex)) else { return }
        wrench.position = lug.position
        turnLug(lugIndex, progress: progress, removed: removed)
    }

    public func moveCameraToDriverEye(camera: Entity) {
        guard let marker = entity(named: "MARKER_DriverEye") else { return }
        camera.transform = marker.transform
        camera.transform.translation += [0, 0, 0.02]
    }

    public func updateLook(camera: Entity, deltaYaw: Float, deltaPitch: Float) {
        var angles = camera.components[LookAnglesComponent.self] ?? LookAnglesComponent()
        angles.yaw = (angles.yaw + deltaYaw).clamped(to: -1.25...1.25)
        angles.pitch = (angles.pitch + deltaPitch).clamped(to: -0.55...0.40)
        camera.components.set(angles)
        camera.orientation = simd_quatf(angle: angles.yaw, axis: [0, 1, 0])
            * simd_quatf(angle: angles.pitch, axis: [1, 0, 0])
    }

    public func setHazardLights(active: Bool) {
        for name in ["LAMP_Hazard_FL", "LAMP_Hazard_FR", "LAMP_Hazard_RL", "LAMP_Hazard_RR", "LAMP_Hazard_Side_R", "LAMP_Hazard_Side_L"] {
            guard let lamp = entity(named: name) else { continue }
            lamp.scale = active ? [1.12, 1.12, 1.12] : [1, 1, 1]
        }
        if active { playBlinkerAudio() }
    }

    public func loadScene() async {
        do {
            guard let url = Bundle.module.url(forResource: "beyond_school_vehicle_scene", withExtension: "usdz") else {
                validationIssues = ["Missing packaged beyond_school_vehicle_scene.usdz"]
                return
            }
            let entity = try await Entity(contentsOf: url)
            root = entity
            validationIssues = bindInteractiveEntities(in: entity)
            guard let audit = auditWorldBounds(in: entity) else {
                validationIssues.append("World-bounds audit could not resolve wheel, mirror, or road.")
                return
            }
            worldBoundsAudit = audit
            trafficController.install(
                in: entity,
                audio: audioEngine,
                roadHeight: audit.roadHeight,
                laneZ: audit.trafficLaneZ
            )
            mechanicController.install(
                in: entity,
                roadHeight: audit.roadHeight,
                wheelCenter: audit.wheel.center
            )
            installVisualRealism(in: entity, audit: audit)
            isLoaded = validationIssues.isEmpty
        } catch {
            validationIssues = ["USDZ load failed: \(error.localizedDescription)"]
        }
    }

    public func bindInteractiveEntities(in root: Entity) -> [String] {
        var missing: [String] = []
        for name in Self.interactiveNames {
            guard let entity = root.findEntity(named: name) else {
                missing.append(name)
                continue
            }
            let bounds = entity.visualBounds(relativeTo: entity)
            let extents = SIMD3<Float>(
                max(bounds.extents.x, 0.04),
                max(bounds.extents.y, 0.04),
                max(bounds.extents.z, 0.04)
            )
            entity.components.set(CollisionComponent(shapes: [.generateBox(size: extents)]))
            entity.components.set(InputTargetComponent(allowedInputTypes: [.direct, .indirect]))
            #if os(visionOS)
            if #available(visionOS 1.0, *) {
                entity.components.set(HoverEffectComponent())
            }
            #endif
        }
        return missing
    }

    public func entity(named name: String) -> Entity? {
        root?.findEntity(named: name)
    }

    public func auditWorldBounds(in root: Entity) -> WorldBoundsAudit? {
        guard
            let wheel = root.findEntity(named: "WHEEL_RL_FlatTarget"),
            let mirror = root.findEntity(named: "MIRROR_Driver"),
            let road = root.findEntity(named: "Road_Asphalt")
        else { return nil }

        let wheelBounds = wheel.visualBounds(relativeTo: root)
        let mirrorBounds = mirror.visualBounds(relativeTo: root)
        let roadBounds = road.visualBounds(relativeTo: root)
        let roadHeight = roadBounds.min.y
        let lateralSign: Float = mirrorBounds.center.z >= 0 ? 1 : -1
        let laneOffset = max(2.8, min(3.6, roadBounds.extents.z * 0.22))
        let laneZ = mirrorBounds.center.z + lateralSign * laneOffset
        return WorldBoundsAudit(
            wheel: WorldBoundsRecord(min: wheelBounds.min, max: wheelBounds.max),
            mirror: WorldBoundsRecord(min: mirrorBounds.min, max: mirrorBounds.max),
            road: WorldBoundsRecord(min: roadBounds.min, max: roadBounds.max),
            trafficLaneZ: laneZ,
            roadHeight: roadHeight,
            mechanicFeetHeight: roadHeight
        )
    }

    private func installVisualRealism(in root: Entity, audit: WorldBoundsAudit) {
        let sky = ModelEntity(
            mesh: .generateSphere(radius: 40),
            materials: [UnlitMaterial(color: .blue)]
        )
        sky.name = "ProceduralSkyDome"
        root.addChild(sky)

        let sun = Entity()
        sun.name = "ProceduralSun_Key"
        #if os(visionOS)
        sun.components.set(DirectionalLightComponent(color: .white, intensity: nightRecallEnabled ? 350 : 2_400))
        #else
        sun.components.set(DirectionalLightComponent(color: .white, intensity: nightRecallEnabled ? 350 : 2_400, isRealWorldProxy: false))
        #endif
        sun.orientation = simd_quatf(angle: -0.65, axis: [1, 0, 0])
            * simd_quatf(angle: 0.45, axis: [0, 1, 0])
        root.addChild(sun)

        let fill = Entity()
        fill.name = "ProceduralSkyFill"
        fill.components.set(PointLightComponent(intensity: nightRecallEnabled ? 80 : 350, attenuationRadius: 18))
        fill.position = [audit.wheel.center.x, audit.roadHeight + 4, audit.wheel.center.z]
        root.addChild(fill)

        addContactShadow(
            named: "ContactShadow_Vehicle",
            to: root,
            center: [audit.wheel.center.x, audit.roadHeight + 0.006, audit.wheel.center.z],
            size: [3.8, 1.8]
        )
        for vehicle in trafficController.vehicles {
            addContactShadow(
                named: "ContactShadow_\(vehicle.identifier)",
                to: root,
                center: [vehicle.x, audit.roadHeight + 0.008, audit.trafficLaneZ],
                size: [2.8, 1.5]
            )
        }
    }

    private func addContactShadow(
        named name: String,
        to root: Entity,
        center: SIMD3<Float>,
        size: SIMD2<Float>
    ) {
        guard root.findEntity(named: name) == nil else { return }
        let shadow = ModelEntity(
            mesh: .generatePlane(width: size.x, depth: size.y),
            materials: [SimpleMaterial(color: .black, isMetallic: false)]
        )
        shadow.name = name
        shadow.position = center
        shadow.scale = [1, 1, 0.55]
        root.addChild(shadow)
    }

    public func animate(named name: String, rotation: simd_quatf? = nil, translation: SIMD3<Float>? = nil, duration: TimeInterval = 0.35) {
        guard let entity = entity(named: name) else { return }
        var transform = entity.transform
        if let rotation { transform.rotation = rotation }
        if let translation { transform.translation = translation }
        entity.move(to: transform, relativeTo: entity.parent, duration: duration, timingFunction: .easeInOut)
    }

    public func playBlinkerAudio() {
        guard let root else { return }
        guard let url = Bundle.module.url(forResource: "blinker01", withExtension: "wav") else { return }
        do {
            let configuration = AudioFileResource.Configuration(
                loadingStrategy: .preload,
                shouldLoop: false
            )
            let resource = try AudioFileResource.load(
                contentsOf: url,
                withName: "blinker01",
                configuration: configuration
            )
            root.playAudio(resource)
        } catch {
            validationIssues.append("Blinker audio failed: \(error.localizedDescription)")
        }
    }

    public func playDoorAudio(opening: Bool) {
        guard let root else { return }
        let name = opening ? "door_opening" : "door_closing"
        guard let url = Bundle.module.url(forResource: name, withExtension: "wav") else { return }
        do {
            let resource = try AudioFileResource.load(
                contentsOf: url,
                withName: name,
                configuration: AudioFileResource.Configuration(loadingStrategy: .preload, shouldLoop: false)
            )
            root.playAudio(resource)
        } catch {
            validationIssues.append("Door audio failed: \(error.localizedDescription)")
        }
    }

    private func attachAudioCue(_ cue: SpatialAudioEngine.Cue, to name: String) {
        guard let entity = entity(named: name) else {
            audioEngine.attach(cue, toEntityNamed: name)
            return
        }
        audioEngine.attach(cue, to: entity, name: name)
    }

    private func applyKinematics(to root: Entity) {
        if let chassis = root.findEntity(named: "BODY_ExteriorShell") {
            chassis.transform.rotation = simd_quatf(angle: kinematics.snapshot.chassisRoll, axis: [0, 0, 1])
                * simd_quatf(angle: kinematics.snapshot.chassisPitch, axis: [1, 0, 0])
                * simd_quatf(angle: kinematics.snapshot.wakeRoll, axis: [1, 0, 0])
            chassis.transform.translation.y = kinematics.snapshot.chassisLift
        }
        if let jackPivot = root.findEntity(named: "TOOL_ScissorJack_UpperArms_Pivot") {
            jackPivot.transform.rotation = simd_quatf(angle: -0.55 * kinematics.snapshot.jackProgress, axis: [0, 0, 1])
        }
        if let wheel = root.findEntity(named: "WHEEL_RL_FlatTarget") {
            wheel.transform.translation.y = kinematics.snapshot.flatWheelPull * kinematics.wheelPullDistance
            wheel.transform.rotation = simd_quatf(angle: -0.35 * kinematics.snapshot.flatWheelPull, axis: [0, 0, 1])
        }
        if let spare = root.findEntity(named: "WHEEL_Spare_Pivot") {
            spare.transform.translation.y = -0.30 + kinematics.snapshot.spareSwap * 0.30
            spare.transform.translation.z = 0.44 + kinematics.snapshot.spareSwap * 0.32
        }
        for (index, state) in kinematics.snapshot.lugs {
            guard let lug = root.findEntity(named: String(format: "LUG_RL_Nut_%02d_Pivot", index)) else { continue }
            lug.transform.rotation = simd_quatf(angle: state.rotation, axis: [0, 1, 0])
            lug.transform.translation.y = state.outward
        }
    }

    private func lugIndex(from name: String) -> Int? {
        guard name.hasPrefix("LUG_RL_Nut_"), let value = Int(name.dropFirst("LUG_RL_Nut_".count).prefix(2)) else {
            return nil
        }
        return value
    }
}

private struct SceneLightingModeComponent: Component {
    var isNight: Bool
}

private struct LookAnglesComponent: Component {
    var yaw: Float = 0
    var pitch: Float = 0
}

private extension Comparable {
    func clamped(to range: ClosedRange<Self>) -> Self {
        min(max(self, range.lowerBound), range.upperBound)
    }
}

private extension Array {
    subscript(safe index: Index) -> Element? {
        indices.contains(index) ? self[index] : nil
    }
}

private extension Entity {
    func findEntity(named name: String) -> Entity? {
        if self.name == name { return self }
        for child in children {
            if let match = child.findEntity(named: name) { return match }
        }
        return nil
    }
}
#else
@MainActor
public final class RealitySceneController {
    public private(set) var isLoaded = false
    public private(set) var validationIssues = ["RealityKit is unavailable on this build host."]
    public init() {}
    public func loadScene() async {}
}
#endif
