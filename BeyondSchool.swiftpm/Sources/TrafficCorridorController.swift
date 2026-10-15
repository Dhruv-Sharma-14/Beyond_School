import Foundation
import simd

#if canImport(RealityKit)
import RealityKit
#endif

@MainActor
public final class TrafficCorridorController {
    public struct Vehicle: Sendable, Equatable {
        public let identifier: String
        public var x: Float
        public let speed: Float

        public init(identifier: String, x: Float, speed: Float) {
            self.identifier = identifier
            self.x = x
            self.speed = speed
        }
    }

    public let laneY: Float = -3.6
    public let dangerZone: ClosedRange<Float> = -18...4
    public private(set) var roadHeight: Float = 0
    public private(set) var laneZ: Float = 0
    public private(set) var wheelBottomHeight: Float = 0
    public private(set) var vehicles: [Vehicle] = [
        Vehicle(identifier: "TrafficVehicle_Sedan", x: -24, speed: 7.0),
        Vehicle(identifier: "TrafficVehicle_Truck", x: -10, speed: 8.5)
    ]
    public private(set) var lastWakeImpulse: Float = 0

    public init() {}

    public var isDangerZoneOccupied: Bool {
        vehicles.contains { dangerZone.contains($0.x) }
    }

    public func update(deltaTime: Float) {
        guard deltaTime > 0 else { return }
        lastWakeImpulse = 0
        for index in vehicles.indices {
            let previousX = vehicles[index].x
            vehicles[index].x += vehicles[index].speed * deltaTime
            if previousX < 3.5, vehicles[index].x >= -3.5 {
                lastWakeImpulse = vehicles[index].identifier == "TrafficVehicle_Truck" ? -1 : 1
            }
            if vehicles[index].x > 24 {
                vehicles[index].x = -24
            }
        }
    }

    public func resetForSmokeTest(positions: [Float]) {
        for (index, position) in positions.prefix(vehicles.count).enumerated() {
            vehicles[index].x = position
        }
    }

    #if canImport(RealityKit)
    public func install(in root: Entity, audio: SpatialAudioEngine, roadHeight: Float, laneZ: Float) {
        self.roadHeight = roadHeight
        self.laneZ = laneZ
        for vehicle in vehicles {
            let entity = makeVehicleEntity(identifier: vehicle.identifier)
            entity.position = [vehicle.x, roadHeight, laneZ]
            root.addChild(entity)
            audio.attach(.trafficWhoosh, to: entity, name: vehicle.identifier)
        }
    }

    public func synchronize(in root: Entity, deltaTime: Float) {
        update(deltaTime: deltaTime)
        for vehicle in vehicles {
            guard let entity = root.findTrafficEntity(named: vehicle.identifier) else { continue }
            entity.position.x = vehicle.x
            entity.position.y = roadHeight
            entity.position.z = laneZ
            entity.findTrafficEntity(named: "\(vehicle.identifier)_Wheel_FL")?.transform.rotation =
                simd_quatf(angle: vehicle.x * 0.8, axis: [0, 1, 0])
        }
    }

    private func makeVehicleEntity(identifier: String) -> Entity {
        let root = Entity()
        root.name = identifier
        let isTruck = identifier.contains("Truck")
        let body = ModelEntity(
            mesh: .generateBox(size: isTruck ? [2.3, 0.9, 0.55] : [1.5, 0.75, 0.45]),
            materials: [SimpleMaterial(color: isTruck ? .white : .darkGray, isMetallic: true)]
        )
        body.name = "\(identifier)_Body"
        body.transform.translation.y = isTruck ? 0.70 : 0.52
        root.addChild(body)
        if isTruck {
            let cargo = ModelEntity(
                mesh: .generateBox(size: [1.25, 0.86, 0.95]),
                materials: [SimpleMaterial(color: .blue, isMetallic: false)]
            )
            cargo.name = "\(identifier)_CargoBox"
            cargo.position = [-0.42, 0, 1.28]
            root.addChild(cargo)
        } else {
            let windshield = ModelEntity(
                mesh: .generateBox(size: [0.52, 0.68, 0.12]),
                materials: [SimpleMaterial(color: .black, isMetallic: true)]
            )
            windshield.name = "\(identifier)_WindshieldTrim"
            windshield.position = [0.10, 0, 0.82]
            root.addChild(windshield)
        }

        for (index, x) in [-0.72, 0.72, -0.72, 0.72].enumerated() {
            let wheel = ModelEntity(
                mesh: .generateCylinder(height: 0.12, radius: isTruck ? 0.18 : 0.14),
                materials: [SimpleMaterial(color: .black, isMetallic: true)]
            )
            wheel.name = "\(identifier)_Wheel_\(["FL", "FR", "RL", "RR"][index])"
            wheel.transform.translation = SIMD3<Float>(
                Float(x),
                isTruck ? 0.18 : 0.14,
                index % 2 == 0 ? -0.43 : 0.43
            )
            wheel.transform.rotation = simd_quatf(angle: .pi / 2, axis: [1, 0, 0])
            root.addChild(wheel)
        }

        let lampMaterial = UnlitMaterial(color: .white)
        let headlamp = ModelEntity(
            mesh: .generateBox(size: [0.12, 0.22, 0.08]),
            materials: [lampMaterial]
        )
        headlamp.name = "\(identifier)_Headlamps"
        headlamp.position = [isTruck ? 1.1 : 0.72, isTruck ? 0.70 : 0.52, -0.22]
        root.addChild(headlamp)

        let tailMaterial = UnlitMaterial(color: .red)
        let taillamp = ModelEntity(
            mesh: .generateBox(size: [0.12, 0.22, 0.08]),
            materials: [tailMaterial]
        )
        taillamp.name = "\(identifier)_Taillamps"
        taillamp.position = [isTruck ? -1.1 : -0.72, isTruck ? 0.70 : 0.52, 0.22]
        root.addChild(taillamp)

        return root
    }
    #endif
}

#if canImport(RealityKit)
private extension Entity {
    func findTrafficEntity(named name: String) -> Entity? {
        if self.name == name { return self }
        for child in children {
            if let match = child.findTrafficEntity(named: name) { return match }
        }
        return nil
    }
}
#endif
