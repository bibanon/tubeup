---
name: Bug report
about: Create a bug report to help us improve
title: 'Bug report: '
labels: bug
assignees: ''

---

**Checklist**

# If you just delete all this text and post a issue it will be closed on sight.

Carefully read and work through this check list in order to prevent the most common mistakes and misuse tubeup, put x into all relevant boxes (like this [x])

- [ ] I have fully updated tubeup, yt-dlp, and internetarchive along with their associated dependencies.
- [ ] I've checked that all URLs and arguments with special characters are properly quoted or escaped
- [ ] I've checked that all provided URLs are alive and playable in a browser
- [ ] If a certain video, audio file, site, or metadata feature does not work, it works in yt-dlp. If not, report it [https://github.com/yt-dlp/yt-dlp/issues](here).
- [ ] I've searched the issues (closed or open) for similar bug reports including closed ones
- [ ] I am not submitting a bug report about S3 timeouts (we have no control over Internet Archive outages or per-user throttling)
- [ ] I've checked the Twitter account of Internet Archive (@internetarchive) for any announced outages or planned infrastructure maintenance that would affect performance of uploads.
- [ ] I have properly indented [with triple backticks before and after the console output](https://guides.github.com/pdfs/markdown-cheatsheet-online.pdf) full terminal terminal output from the line where the command was run to where I was returned to command prompt, and am not trying to obscure item identifiers or URLs used in the creation of the bug (we need this to recreate the bug or investigate what happened).

**Dependency versions**

Please provide version information from core dependencies:

`ia --version`

**Expected behavior**
A clear and concise description of what you expected to happen.

**Additional context**
Add any other context about the problem here.
