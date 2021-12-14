[![Build Status](https://travis.ibm.com/Whitewater/whitewater-detect-secrets.svg?token=tSTYkwXezbKBusqJ3V4L&branch=master)](https://travis.ibm.com/Whitewater/whitewater-detect-secrets)

# Whitewater Detect Secrets

## About

IBM `detect-secrets` is a client-side security tool built for developers, and is designed to **detect secrets** within a codebase for the sake of remediation and prevention of secret leaks.

This is a fork of [detect-secrets from Yelp](https://github.com/Yelp/detect-secrets). Our version includes additional detection, some of which is unique to IBM, as well as additional features to help integrate with IBM services.

Unlike other similar packages that solely focus on finding secrets,
this package is designed with the enterprise client in mind,
providing a backwards-compatible, systematic means of:

1. **Detecting secret leaks.** Scan a repository to find and remediate existing secrets within its source code.
2. **Preventing secret leaks.** Prevent new secrets from entering the repository via a pre-commit hook.

This way, you create a
[separation of concern](https://en.wikipedia.org/wiki/Separation_of_concerns):
understanding that there may _currently_ be secrets hiding in your large repository
(this is what we refer to as a _baseline_),
while also preventing the issue from getting any larger.

It does this by running periodic diff outputs against heuristically-crafted
regex statements, to identify whether any _new_ secret has been committed. This
way, it avoids the overhead of digging through all git history, as well as the
need to scan the entire repository every time.

For a look at recent changes, please see the
[changelog](/CHANGELOG.md).
(Note: the upstream Yelp community maintains this but we historically have not done so within IBM.)

## Requirements

Python 3

### Install/Upgrade Module

`pip install --upgrade "git+https://github.com/ibm/detect-secrets.git@master#egg=detect-secrets"`

## Usage

`detect-secrets` comes with three different tools, and there is often confusion around which one
to use. Use this handy checklist to help you decide:

1. Do you want to add secrets to your baseline? If so, use **`detect-secrets scan`**.
2. Do you want to alert off new secrets not in the baseline? If so, use **`detect-secrets-hook`**.
3. Are you analyzing the baseline itself? If so, use **`detect-secrets audit`**.

### Adding Secrets to Baseline

```
$ detect-secrets scan --help
usage: detect-secrets scan [-h] [--exclude-lines EXCLUDE_LINES] [--word-list WORD_LIST_FILE] [--exclude-files EXCLUDE_FILES] [--update OLD_BASELINE_FILE] [--use-all-plugins] [--all-files] [-n] [--output-verified-false] [--string [STRING]]
                           [--output-raw] [--base64-limit [BASE64_LIMIT]] [--hex-limit [HEX_LIMIT]] [--no-hex-string-scan] [--no-base64-string-scan] [--no-private-key-scan] [--no-basic-auth-scan] [--no-keyword-scan] [--no-aws-key-scan]
                           [--no-slack-scan] [--no-artifactory-scan] [--no-stripe-scan] [--no-mailchimp-scan] [--no-jwt-scan] [--no-box-scan] [--no-cloudant-scan] [--no-ghe-scan] [--no-softlayer-scan] [--no-ibm-cloud-iam-scan]
                           [--no-ibm-cos-hmac-scan] [--no-twilio-key-scan] [--no-npm-scan] [--no-square-oauth] [--no-azure-storage-scan] [--no-github-scan] [--db2-scan] [--keyword-exclude KEYWORD_EXCLUDE] [--ghe-instance GHE_INSTANCE]
                           [path ...]

positional arguments:
  path                  Scans the entire codebase and outputs a snapshot of currently identified secrets.

optional arguments:
  -h, --help            show this help message and exit
  --exclude-lines EXCLUDE_LINES
                        Pass in regex to specify lines to ignore during scan.
  --word-list WORD_LIST_FILE
                        Text file with a list of words, if a secret contains a word in the list we ignore it.
  --exclude-files EXCLUDE_FILES
                        Pass in regex to specify ignored paths during initialization scan.
  --update OLD_BASELINE_FILE
                        Update existing baseline by importing settings from it.New file would be created if old baseline file does not exist.
  --use-all-plugins     Use all available plugins to scan files.
  --all-files           Scan all files recursively (as compared to only scanning git tracked files).
  -n, --no-verify       Disables additional verification of secrets via network call.
  --output-verified-false
                        Output secrets that are verified false.
  --string [STRING]     Scans an individual string, and displays configured plugins' verdict.
  --output-raw          Outputs the raw secret in the baseline file.For development/extension purposes.Do not use this option in a repo monitoring context.

plugins:
  Configure settings for each secret scanning ruleset. By default, all plugins are enabled unless explicitly disabled.

  --base64-limit [BASE64_LIMIT]
                        Sets the entropy limit for high entropy strings. Value must be between 0.0 and 8.0, defaults to 4.5.
  --hex-limit [HEX_LIMIT]
                        Sets the entropy limit for high entropy strings. Value must be between 0.0 and 8.0, defaults to 3.0.
  --no-hex-string-scan  Disables scanning for hex high entropy strings
  --no-base64-string-scan
                        Disables scanning for base64 high entropy strings
  --no-private-key-scan
                        Disables scanning for private keys.
  --no-basic-auth-scan  Disables scanning for Basic Auth formatted URIs.
  --no-keyword-scan     Disables scanning for secret keywords.
  --no-aws-key-scan     Disables scanning for AWS keys.
  --no-slack-scan       Disables scanning for Slack tokens.
  --no-artifactory-scan
                        Disable scanning for Artifactory credentials
  --no-stripe-scan      Disable scanning for Stripe keys
  --no-mailchimp-scan   Disable scanning for Mailchimp keys
  --no-jwt-scan         Disable scanning for JWTs
  --no-box-scan         Disables scans for Box credentials
  --no-cloudant-scan    Disables scans for Cloudant credentials
  --no-ghe-scan         Disables scans for GitHub Enterprise credentials
  --no-softlayer-scan   Disables scans for SoftLayer credentials
  --no-ibm-cloud-iam-scan
                        Disables scans for IBM Cloud IAM credentials
  --no-ibm-cos-hmac-scan
                        Disables scans for IBM Cloud Object Storage HMAC keys
  --no-twilio-key-scan  Disables scans for Twilio API keys.
  --no-npm-scan         Disables scans for NPM keys.
  --no-square-oauth     Disables scans for Square OAuth tokens.
  --no-azure-storage-scan
                        Disables scans for Azure Storage Account access.
  --no-github-scan      Disables scans for GitHub credentials
  --db2-scan            Enable scanning for DB2 Tokens
  --keyword-exclude KEYWORD_EXCLUDE
                        Pass in regex to exclude false positives found by keyword detector.
  --ghe-instance GHE_INSTANCE
                        Instance URL for GHE i.e. github.ibm.com
```

### Blocking Secrets not in Baseline

```
$ detect-secrets-hook --help
usage: detect-secrets-hook [-h] [-v] [--version] [--baseline BASELINE] [--exclude-lines EXCLUDE_LINES] [--word-list WORD_LIST_FILE] [--use-all-plugins] [-n] [--output-verified-false] [--fail-on-non-audited] [--base64-limit [BASE64_LIMIT]]
                           [--hex-limit [HEX_LIMIT]] [--no-hex-string-scan] [--no-base64-string-scan] [--no-private-key-scan] [--no-basic-auth-scan] [--no-keyword-scan] [--no-aws-key-scan] [--no-slack-scan] [--no-artifactory-scan]
                           [--no-stripe-scan] [--no-mailchimp-scan] [--no-jwt-scan] [--no-box-scan] [--no-cloudant-scan] [--no-ghe-scan] [--no-softlayer-scan] [--no-ibm-cloud-iam-scan] [--no-ibm-cos-hmac-scan] [--no-twilio-key-scan]
                           [--no-npm-scan] [--no-square-oauth] [--no-azure-storage-scan] [--no-github-scan] [--db2-scan] [--keyword-exclude KEYWORD_EXCLUDE] [--ghe-instance GHE_INSTANCE]
                           [filenames ...]

positional arguments:
  filenames             Filenames to check.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose mode.
  --version             Display version information.
  --baseline BASELINE   Sets a baseline for explicitly ignored secrets, generated by `--scan`.
  --exclude-lines EXCLUDE_LINES
                        Pass in regex to specify lines to ignore during scan.
  --word-list WORD_LIST_FILE
                        Text file with a list of words, if a secret contains a word in the list we ignore it.
  --use-all-plugins     Use all available plugins to scan files.
  -n, --no-verify       Disables additional verification of secrets via network call.
  --output-verified-false
                        Output secrets that are verified false.
  --fail-on-non-audited
                        Fail check if there are entries have not been audited in baseline.

plugins:
  Configure settings for each secret scanning ruleset. By default, all plugins are enabled unless explicitly disabled.

  --base64-limit [BASE64_LIMIT]
                        Sets the entropy limit for high entropy strings. Value must be between 0.0 and 8.0, defaults to 4.5.
  --hex-limit [HEX_LIMIT]
                        Sets the entropy limit for high entropy strings. Value must be between 0.0 and 8.0, defaults to 3.0.
  --no-hex-string-scan  Disables scanning for hex high entropy strings
  --no-base64-string-scan
                        Disables scanning for base64 high entropy strings
  --no-private-key-scan
                        Disables scanning for private keys.
  --no-basic-auth-scan  Disables scanning for Basic Auth formatted URIs.
  --no-keyword-scan     Disables scanning for secret keywords.
  --no-aws-key-scan     Disables scanning for AWS keys.
  --no-slack-scan       Disables scanning for Slack tokens.
  --no-artifactory-scan
                        Disable scanning for Artifactory credentials
  --no-stripe-scan      Disable scanning for Stripe keys
  --no-mailchimp-scan   Disable scanning for Mailchimp keys
  --no-jwt-scan         Disable scanning for JWTs
  --no-box-scan         Disables scans for Box credentials
  --no-cloudant-scan    Disables scans for Cloudant credentials
  --no-ghe-scan         Disables scans for GitHub Enterprise credentials
  --no-softlayer-scan   Disables scans for SoftLayer credentials
  --no-ibm-cloud-iam-scan
                        Disables scans for IBM Cloud IAM credentials
  --no-ibm-cos-hmac-scan
                        Disables scans for IBM Cloud Object Storage HMAC keys
  --no-twilio-key-scan  Disables scans for Twilio API keys.
  --no-npm-scan         Disables scans for NPM keys.
  --no-square-oauth     Disables scans for Square OAuth tokens.
  --no-azure-storage-scan
                        Disables scans for Azure Storage Account access.
  --no-github-scan      Disables scans for GitHub credentials
  --db2-scan            Enable scanning for DB2 Tokens
  --keyword-exclude KEYWORD_EXCLUDE
                        Pass in regex to exclude false positives found by keyword detector.
  --ghe-instance GHE_INSTANCE
                        Instance URL for GHE i.e. github.ibm.com
```

We recommend setting this up as a pre-commit hook. One way to do this is by using the
[pre-commit](https://github.com/pre-commit/pre-commit) framework:

```yaml
# .pre-commit-config.yaml
- repo: https://github.com/ibm/detect-secrets
  # If you desire to use a specific version of detect-secrets, you can replace `master` with other git revisions such as branch, tag or commit sha.
  # You are encouraged to use static refs such as tags, instead of branch name
  #
  # Running "pre-commit autoupdate" would automatically updates rev to latest tag
  rev: master
  hooks:
      - id: detect-secrets # pragma: whitelist secret
        # Add options for detect-secrets-hook binary. You can run `detect-secrets-hook --help` to list out all possible options.
        # You may also run `pre-commit run detect-secrets` to preview the scan result.
        # when "--baseline" without "--use-all-plugins", pre-commit scan with just plugins in baseline file
        # when "--baseline" with "--use-all-plugins", pre-commit scan with all available plugins
        # add "--fail-on-non-audited" to fail pre-commit for unaudited potential secrets
        args: [--baseline, .secrets.baseline, --use-all-plugins]
```

#### Inline Allowlisting

There are times when we want to exclude a false positive from blocking a commit, without creating
a baseline to do so. You can do so by adding a comment as such:

```python
secret # pragma: allowlist secret
secret // pragma: allowlist secret
secret /* pragma: allowlist secret */
secret ' pragma: allowlist secret
secret -- pragma: allowlist secret
secret <!-- pragma: allowlist secret -->
secret <!-- # pragma: allowlist secret -->
```

or

```javascript
//  pragma: allowlist nextline secret
const secret = "hunter2";
```

### Auditing Secrets in Baseline

```bash
$ detect-secrets audit --help
usage: detect-secrets audit [-h] [--diff | --display-results] filename [filename ...]

positional arguments:
  filename           Audit a given baseline file to distinguish the difference between false and true positives.

optional arguments:
  -h, --help         show this help message and exit
  --diff             Allows the comparison of two baseline files, in order to effectively distinguish the difference between various plugin configurations.
  --display-results  Displays the results of an interactive auditing session which have been saved to a baseline file.
```

### Detection: Setting Up a Baseline

After installing detect-secrets, run the following command from within the root directory of a given repository to scan it for existing secrets, logging the results in `.secrets.baseline`.

```
$ detect-secrets scan --update .secrets.baseline
```

Note: You may run this same command again to re-scan the repo and update the baseline file.

### Detection: Auditing a Baseline

Run the following command to audit `.secrets.baseline`, marking secrets as true positives or false positives. Remove true positives from your codebase, revoking them if they've been leaked remotely.

```
$ detect-secrets audit .secrets.baseline
Secret:      1 of 80
Filename:    test_data/baseline.file
Secret Type: Secret Keyword
----------
59:    }
60:  ],
61:  "results": {
62:    "config.env": [
63:      {
64:        "hashed_secret": "513e0a36963ae1e8431c041b744679ee578b7c44",
65:        "is_verified": false,
66:        "line_number": 1,
67:        "type": "Base64 High Entropy String"
68:      }
69:    ],
----------
Is this a valid secret? i.e. not a false-positive (y)es, (n)o, (s)kip, (q)uit:
```

Commit the `.secrets.baseline` file to your repo with remediated files after auditing.

When interactively auditing a baseline, if you label a secret as a valid secret. It is expected that you have remediated that secret. This is intended for historical bookkeeping purposes and assumes that the user has revoked the token / secret since remediated tokens will still be viewable in the repo's commit history.

### Detection: Reducing False Positives during Baseline Scan

Use the built-in help command `detect-secrets scan --help` to identify ways of excluding files, lines, or plugins that are generating too many false positives. Note that this comes with a security trade-off.

Also see [inline allowlisting](#inline-allowlisting) for instructions on excluding individual lines via in-line comments.

### Prevention: pre-commit Hook

A pre-commit hook can automatically run `detect-secrets` against new commits in your local repository at commit-time. The purpose of this is to prevent additional secrets from being leaked.

Configuration steps (per-developer, per-repo, must have created `.secrets.baseline` file first):

-   If not installed, install the `pre-commit` Python module (ex. `pip install pre-commit`).
-   If `.pre-commit-config.yaml` not already present, copy the text from this [example pre-commit configuration](/user-config/.pre-commit-config.yaml)
    into a file called `.pre-commit-config.yaml` at the root of the repository where you want to setup the pre-commit hook.
-   Finally, run `pre-commit install` in the root of the repo to set up the pre-commit hook based on the specifications in `.pre-commit-config.yaml`.

You may use the built-in help command `detect-secrets-hook --help` to identify additional arguments you can pass to the pre-commit script. These arguments must be passed via the `args` section of `.pre-commit-config.yaml`. Ex:

```
rev: master
  hooks:
    - id: detect-secrets
      args: [ --argument1, --argument2 ]
```

### Command Line

`detect-secrets` is designed to be used as a git pre-commit hook, but you can also invoke `detect-secrets scan [path]` directly, `path` being the file(s) and/or directory(ies) to scan (`path` defaults to `.` if not specified).

It should be noted that by default, `detect-secrets scan` only operates on files that are tracked by git. So if you intend to scan files outside of a git repository, you will need to pass the `--all-files` flag.

#### Inline Allowlisting

To tell `detect-secrets` to ignore a particular line of code, simply append an
inline `pragma: allowlist secret` comment. For example:

```python
API_KEY = "blah-blah-but-actually-not-secret"  # pragma: allowlist secret
print('hello world')
```

Inline commenting syntax for a multitude of languages is supported:

| Comment Style |       Language Support        |
| :-----------: | :---------------------------: |
|      `#`      | e.g. Python, Dockerfile, YAML |
|     `//`      |      e.g. Go, C++, Java       |
|    `/* */`    |         e.g. C, Java          |
|      `'`      |    e.g. Visual Basic .NET     |
|     `--`      |       e.g. SQL, Haskell       |
|  `<!-- -->`   |           e.g. XML            |

This may be a convenient way for you to allowlist secrets, without having to
regenerate the entire baseline again. Furthermore, this makes the allowlisted
secrets easily searchable, auditable, and maintainable.

### User Guide

If you are an IBMer looking for more information on how to use this project as an end user please refer to the [user guide](https://w3.ibm.com/w3publisher/detect-secrets/developer-tool). Within this repo, see [docs](/docs) for an FAQ and cheat-sheet.

## Caveats

This is not meant to be a sure-fire solution to prevent secrets from entering
the codebase. Only proper developer education can truly do that. This pre-commit
hook merely implements several heuristics to try and prevent obvious cases of
committing secrets.

### Things that won't be prevented

-   Secrets that don't trigger any of the enabled plugins.

### Plugin Configuration

One method that this package uses to find secrets is by searching for high
entropy strings in the codebase. This is calculated through the [Shannon entropy
formula](http://blog.dkbza.org/2007/05/scanning-data-for-entropy-anomalies.html).
If the entropy of a given string exceeds the preset amount, the string will be
rejected as a potential secret.

This preset amount can be adjusted in several ways:

-   Specifying it within a config file (`.secrets.baseline`, `.pre-commit-config.yaml`).
-   Specifying it with command line flags (e.g. `--base64-limit`)

Lowering these limits will identify more potential secrets, but also create
more false positives. Adjust these limits to suit your needs.

## Contribution

Please read [CONTRIBUTING.md](/CONTRIBUTING.md). It contains information on how setup a development environment, verify changes, and run the test suite.

## Plugins

Each of the secret checks are developed as plugins in the [detect_secrets/plugins](/detect_secrets/plugins) directory. Each plugin represents a single test or a group of tests.

Refer to the plugin directory above for the list of supported secret detectors.

## IBM versioning and rebase guide

-   [update.md](./update.md)
