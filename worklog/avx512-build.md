# Pinned local CPU build

Built on 22 October 2026 on AMD EPYC 9V74, with a four-core CPU quota and 32 GiB memory limit. The CPU exposes AVX2, AVX512F/DQ/BW/VL, VBMI, VNNI and BF16. Run manifests distinguish this binary from the original AVX2 calibration runtime.

Source: `ggml-org/llama.cpp` revision `a37cc46104eb50900d5ab4a9ba02a0abdac039db`. Archive SHA-256: `784ada1e55d180e1ba26dbe37b881232bf259fd5b866a0ac28f8d2f9b08d3c1d`. CMake 3.31.6. Source preparation and integrity verification: `scripts/setup_local_inference.sh`.

Exact additional build command, from the repository root:

```sh
GIT_CEILING_DIRECTORIES="$PWD/.cache/inference" .venv/bin/cmake \
  -S .cache/inference/llama.cpp-a37cc46104eb50900d5ab4a9ba02a0abdac039db \
  -B .cache/inference/build-avx512 -DCMAKE_BUILD_TYPE=Release \
  -DGGML_NATIVE=OFF -DGGML_AVX2=ON -DGGML_AVX512=ON \
  -DGGML_AVX512_VBMI=ON -DGGML_AVX512_VNNI=ON -DGGML_AVX512_BF16=ON \
  -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=OFF -DLLAMA_BUILD_APP=OFF \
  -DLLAMA_BUILD_UI=OFF -DLLAMA_USE_PREBUILT_UI=OFF
.venv/bin/cmake --build .cache/inference/build-avx512 --target llama-server -j 3
```

Build completed successfully. Binary/shared-library hashes are recorded in runtime manifests. The archive has no upstream Git metadata; the executable reports build 0 / commit unknown. The source pin and archive verification establish provenance. Bitwise reproducibility across compilers/architectures is not claimed. The embedding service used the AVX2 binary throughout development.
