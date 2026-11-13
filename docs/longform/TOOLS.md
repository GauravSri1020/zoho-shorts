# Long-video tools - licence check (13 Nov 2026, scheduled run)

Channel will be MONETIZED = commercial use. Rule: code licence AND model-weights licence must both allow it.
Checked on GitHub LICENSE / README files and Hugging Face model cards (13 Nov 2026). "unverified" = could not confirm.

## Voice (tonight - one fixed voice for the whole video)
| Tool | Code | Weights | Commercial | CPU | Decision |
|---|---|---|---|---|---|
| **Kokoro-82M** via `kokoro-onnx` | MIT (wrapper), Apache-2.0 (Kokoro) | Apache-2.0 | YES | measured RTF 0.70 on 2 cores (8 min audio ~ 6 min) | **USED** - voice `am_michael` (US male). No Indian-English voice exists in Kokoro. |
| Piper (`piper-tts`, OHF-Voice/piper1-gpl) | GPL-3.0 | per voice! | only some voices | fast | fallback only: en_US-ljspeech / joe / mike / kathleen (PD / CC0). NOT lessac (research-only), NOT en_GB-alan. |

Links: https://github.com/hexgrad/kokoro , https://huggingface.co/hexgrad/Kokoro-82M , https://github.com/thewh1teagle/kokoro-onnx , https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/COMMERCIAL_USE.md

## Voice CLONING (Gaurav's own voice, with his consent - after he sends a 1-2 min sample)
| Tool | Code | Weights | Commercial | Notes |
|---|---|---|---|---|
| **Chatterbox** (Resemble AI; Turbo 350M / Nano 110M) | MIT | MIT | YES | every output has the inaudible PerTh watermark (fine for own voice). Repo now archived (no updates). Nano: "3x realtime on 8 CPU cores" (vendor) -> ~1x on a 4-core runner (unverified). **First choice.** |
| **OpenVoice V2** (MyShell) + MeloTTS | MIT | MIT ("free for commercial use") | YES | lighter; test side by side with Chatterbox. |
| CosyVoice2 | Apache-2.0 | Apache-2.0 (card disclaimer says "academic") | unclear | skip unless the above fail |
| Fish-Speech / OpenAudio | Fish Community Licence (13 Oct 2026) | same | only < USD 500k revenue + "Built with Fish Audio" credit | skip |
| IndexTTS2 | bilibili licence | same | royalty-free below big-company limits | GPU-oriented |
| XTTS-v2 | MPL-2.0 | **CPML = non-commercial** | NO | excluded (Coqui closed - no commercial licence can be bought) |
| F5-TTS | MIT | **CC-BY-NC-4.0** | NO | excluded |

## Lip-sync for the small presenter corner (~360 px face)
| Tool | Licence | Commercial | CPU | Decision |
|---|---|---|---|---|
| Wav2Lip | LRS2 - "commercial use strictly prohibited" | NO | - | never |
| LatentSync 1.5/1.6 | Apache-2.0 code, but uses **InsightFace** models (non-commercial) | NO as shipped | needs 8-18 GB VRAM | no |
| LivePortrait / Hallo | MIT code, InsightFace inside | NO as shipped | GPU | no |
| MuseTalk 1.5 | MIT, weights "any purpose, even commercially" (deps sd-vae / whisper / dwpose permissive per secondary sources) | likely YES | GPU only in practice (8 min = 12k frames -> hours on CPU) | later, only with a GPU |
| SadTalker | Apache-2.0 (3DMM/BFM part unverified) | uncertain | slow | no |
| Rhubarb Lip Sync | MIT | YES | fast | needs drawn mouth shapes - not for a real photo |

**Decision tonight:** no licence-clean neural lip-sync runs on this CPU in reasonable time. The corner shows Gaurav's real cut-out
photo (assets/presenter) with breathing / sway, a mic, and a voice level meter - NO fake mouth movement.
Next options: (a) Flow base clip loop of Gaurav at the mic (1-2 Flow clips) + MuseTalk on a free GPU (Kaggle not wanted by Gaurav) ;
(b) keep the photo corner. Gaurav decides after the sample.

## Visuals / audio
- Scenes: HTML + SVG with deterministic `window.render(t)`, Playwright screenshots -> ffmpeg (libx264). All own code.
- Fonts (committed in longform/fonts with OFL.txt): Inter, Kalam, Caveat - SIL Open Font License 1.1 (google/fonts `ofl/`).
- Music: generated on the fly by `autopilot/music.py` (repo's own synth = no copyright claim). Sound effects: synthesised in longform/render.py.
- Screens: Gaurav's own Zoho Books screenshots (assets/screens/books, demo org "Helios", sample data).
