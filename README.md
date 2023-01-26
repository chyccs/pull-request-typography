# Pull-Request-Typography

[![Maintainability](https://api.codeclimate.com/v1/badges/34344560ee25623f7761/maintainability)](https://codeclimate.com/github/chyccs/pull-request-typography/maintainability)
[![DeepSource](https://deepsource.io/gh/chyccs/pull-request-typography.svg/?label=active+issues&show_trend=true&token=9jw18ddlKbv2Gr9MKxFHrsLo)](https://deepsource.io/gh/chyccs/pull-request-typography/?ref=repository-badge)

### Usage

```yaml
  - name: Pull-Request-Typography
    uses: chyccs/pull-request-typography@master
    continue-on-error: true
    with:
        src_path: "."
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
