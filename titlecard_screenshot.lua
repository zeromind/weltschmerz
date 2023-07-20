-- use in mpv via keybind in input.conf: e.g. F11 script-message-to titlecard_screenshot take_titlecard_screenshot 1
-- creates screenshot with sha1 of source filename, to not run into file name length limits for the screenshot file
-- TODO: expose screenshot basedir and extension as script-opts
-- TODO: either
-- * use lua native function for trimming filnames, while keeping crc32 (suggested by Dagger)
-- * include lua-native hashing function
function get_screenshot_target_path(source_filename, time_pos)
    local screenshot_basepath = "/anime/screenshots/unsorted/"
    local screenshot_extension = "jpg"
    local r =
        mp.command_native(
        {
            name = "subprocess",
            playback_only = false,
            capture_stdout = true,
            stdin_data = source_filename,
            args = {"sha1sum"}
        }
    )
    if r.status == 0 then
        local csum = r.stdout:match("^(.-) ")
        local screenshot_file_path =
            string.format("%s%s_%s.%s", screenshot_basepath, csum, time_pos, screenshot_extension)
        return screenshot_file_path
    end
    return string.format("%s%s_%s.%s", screenshot_basepath, filename, time_pos, screenshot_extension)
end

-- titlecard type: 1 = ep, 2 = anime, 4 = ep preview
function take_titlecard_screenshot(titlecard_type, done_command)
    local source_filename = mp.get_property_native("filename")
    local time_pos = mp.get_property("time-pos")
    local screenshot_file_path = get_screenshot_target_path(source_filename, time_pos)
    mp.commandv("screenshot-to-file", screenshot_file_path, "video")
    local r =
        mp.command_native(
        {
            name = "subprocess",
            playback_only = false,
            capture_stdout = true,
            args = {
                "/usr/bin/python3",
                "/anime/screenshots/tag-anime-screenshot.py",
                "-S",
                screenshot_file_path,
                "-F",
                mp.get_property("path"),
                "-s",
                mp.get_property("file-size"),
                "-d",
                mp.get_property_osd("duration"),
                "-D",
                mp.get_property("duration"),
                "-t",
                mp.get_property_osd("time-pos"),
                "-T",
                mp.get_property("time-pos"),
                "--screenshot-type",
                titlecard_type
            }
        }
    )
    print(r.stdout)
    if done_command then
        mp.command(done_command)
    end
end

mp.register_script_message("take_titlecard_screenshot", take_titlecard_screenshot)
