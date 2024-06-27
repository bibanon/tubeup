---
name: Bug report
about: Create a bug report to help us improve
title: 'Bug report: '
labels: bug
assignees: ''

---

**Checklist**

# If you just delete all this text and post a issue it will be closed on sight.

Carefully read and work through this check list in order to prevent the most common mistakes and misuse of tubeup, put x into all relevant boxes (like this [x])

- [ ] I understand Tubeup is merely a middleman between `yt-dlp` and `internetarchive`, and relies on said package dependiencies functioning properly, for example: Site extractors in `yt-dlp` become stale or sites change layout breaking regex, and `internetarchive` has outages or throttles users S-3 access, and that these things are beyond the control of the maintainers of Tubeup.
- [ ] I've updated `tubeup`, `yt-dlp` and `internetarchive` along with their associated dependencies to their latest versions as supported by each afformentioned package setup scripts.
- [ ] I've included the full and unredacted URL and console output (with the exception of site usernames and passwords, or IP addresses of the machine doing the download). I understand hiding URLs will get issue closed on sight.
- [ ] I've checked that all provided URLs are alive, playable in a browser and arguments with special characters are properly quoted or escaped.
- [ ] I've searched the issues (closed or open) for similar bug reports, not just here on Tubeup, but [yt-dlps issue tracker](https://github.com/yt-dlp/yt-dlp/issues) for download issues similar to mine and [internetarchives issue tracker](https://github.com/jjjake/internetarchive/issues) for upload issues similar to mine. YT-DLP has an issue up [listing known bugs](https://github.com/yt-dlp/yt-dlp/issues/3766).
- [ ] I'm not submitting a bug report about IA S3 timeouts (we have no control over Internet Archive outages or per-user throttling, and sometimes the site has maintence like hard disk swaps)
- [ ] I've checked the [X account for Internet Archive](https://x.com/internetarchive) for any announced outages or planned infrastructure maintenance that would affect performance of uploads.
- [ ] I have properly indented [with triple backticks - the key directly below Escape on a QWERTY keyboard - before and after the console output](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#quoting-code) full terminal terminal output from the line where the command was run to where I was returned to command prompt, and am not trying to obscure item identifiers or URLs used in the creation of the bug (we need this to recreate the bug or investigate what happened).

**Dependency versions**

Please provide version information from core dependencies:

yt-dlp version:
`yt-dlp --version`

`internetarchive` python client version:
`ia --version`

Tubeup version:
`tubeup --version`

**Expected behavior**
A clear and concise description of what you expected to happen.

**Additional context**
Add any other context about the problem here.
