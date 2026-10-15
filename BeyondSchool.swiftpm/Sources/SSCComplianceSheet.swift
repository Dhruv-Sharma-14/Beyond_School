import SwiftUI

public struct SSCComplianceSheet: View {
    public init() {}

    public var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 12) {
                Text("SSC Credits & Compliance")
                    .font(.title2.bold())
                Text("Beyond School · Feature 01 roadside emergency trainer")
                    .foregroundStyle(.secondary)
                Text("Asset provenance")
                    .font(.headline)
                Text("Runtime audio and environment sources are documented in ASSET_MANIFEST.md. Staged CC0 sources include Poly Haven environment materials and OpenGameArt vehicle sound effects. The packaged runtime includes only the optimized USDZ and selected WAV files.")
                Text("AI assistance disclosure")
                    .font(.headline)
                Text("Development used AI-assisted code generation and review under human direction. Scene design, safety sequencing, asset selection, validation, and final packaging remain the responsibility of the project author.")
                Text("Safety disclaimer")
                    .font(.headline)
                Text("The 1033 National Highway Assistance reference is educational only. In a real roadside emergency, move to a safe location, follow local traffic rules, and contact the appropriate emergency or highway authority. This simulation does not provide roadside service.")
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding()
        }
        .accessibilityLabel("SSC credits and compliance sheet")
    }
}
