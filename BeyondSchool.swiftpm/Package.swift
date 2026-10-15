// swift-tools-version: 6.0

import PackageDescription

let package = Package(
    name: "BeyondSchool",
    platforms: [
        .macOS(.v15),
        .visionOS(.v2)
    ],
    products: [
        .executable(name: "BeyondSchool", targets: ["BeyondSchool"])
    ],
    targets: [
        .executableTarget(
            name: "BeyondSchool",
            path: "Sources",
            resources: [
                .process("Resources")
            ]
        )
    ]
)
