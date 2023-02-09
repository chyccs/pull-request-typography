# Pull-Request-Typography

[![Maintainability](https://api.codeclimate.com/v1/badges/34344560ee25623f7761/maintainability)](https://codeclimate.com/github/chyccs/pull-request-typography/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/34344560ee25623f7761/test_coverage)](https://codeclimate.com/github/chyccs/pull-request-typography/test_coverage)

[![DeepSource](https://deepsource.io/gh/chyccs/pull-request-typography.svg/?label=active+issues&show_trend=true&token=9jw18ddlKbv2Gr9MKxFHrsLo)](https://deepsource.io/gh/chyccs/pull-request-typography/?ref=repository-badge)

### Usage

```yaml
  - name: Pull-Request-Typography
    uses: chyccs/pull-request-typography@master
    continue-on-error: true
    with:
        src_path: ${{ github.workspace }}
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```


### Bump dependabot pull request title

##### AS-IS
build(deps): bump semgrep from 1.9.0 to 1.10.0
##### TO-BE
build(deps): bump `semgrep` from `1.9.0` to `1.10.0`


### Make conventional title on pull request and keyword highlights

##### AS-IS
(Feat)Extends Singularize And Pluralize Symbols On make_test.py
##### TO-BE
feat: extends `singularize` and `pluralize` symbols on `make_test.py`


### Dependencies
* https://github.com/returntocorp/semgrep
