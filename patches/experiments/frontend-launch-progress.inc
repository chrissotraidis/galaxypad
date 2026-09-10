// Included inside the launch-success branch. Uses only the existing SDL renderer.
const Uint64 launch_started = SDL_GetTicks();
Uint64 next_progress = 0;
bool progress_hidden = false;
bool stop_requested = false;
const auto update_launch_progress = [&] {
  if (progress_hidden || SDL_GetTicks() < next_progress)
    return;
  next_progress = SDL_GetTicks() + 250;
  // This marker follows native runtime-window creation in the current runner.
  // Bound reads even if the child produces a large diagnostic log.
  std::ifstream log(log_path, std::ios::binary | std::ios::ate);
  if (log) {
    const auto length = log.tellg();
    if (length > 0) {
      const auto start = length > std::streamoff(8192) ? length - std::streamoff(8192) : std::streampos(0);
      log.seekg(start);
      std::string tail(static_cast<size_t>(length - start), '\0');
      log.read(tail.data(), static_cast<std::streamsize>(tail.size()));
      if (tail.find("[staticrecomp] module loaded:") != std::string::npos) {
        SDL_HideWindow(window);
        progress_hidden = true;
        return;
      }
    }
  }
  ImGui_ImplSDLRenderer3_NewFrame();
  ImGui_ImplSDL3_NewFrame();
  ImGui::NewFrame();
  const ImGuiViewport* viewport = ImGui::GetMainViewport();
  ImGui::SetNextWindowPos(viewport->WorkPos);
  ImGui::SetNextWindowSize(viewport->WorkSize);
  ImGui::Begin("Starting game", nullptr, ImGuiWindowFlags_NoDecoration |
               ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoSavedSettings);
  ImGui::TextUnformatted(stop_requested ? "Stopping game..." : "Starting GalaxyPad...");
  ImGui::Separator();
  ImGui::Text("Elapsed: %llu seconds", static_cast<unsigned long long>((SDL_GetTicks() - launch_started) / 1000));
  ImGui::TextWrapped("The game window will open when initialization finishes. No second launch is needed.");
  ImGui::End();
  ImGui::Render();
  SDL_SetRenderScale(renderer, io.DisplayFramebufferScale.x, io.DisplayFramebufferScale.y);
  SDL_SetRenderDrawColor(renderer, 18, 20, 28, 255);
  SDL_RenderClear(renderer);
  ImGui_ImplSDLRenderer3_RenderDrawData(ImGui::GetDrawData(), renderer);
  SDL_RenderPresent(renderer);
};
update_launch_progress();
