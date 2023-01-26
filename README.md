# Pull-Request-Typography

[![Build and Test](https://github.com/NeoSmartpen/hwr-api/actions/workflows/on-push.yml/badge.svg?branch=master)](https://github.com/NeoSmartpen/hwr-api/actions/workflows/on-push.yml)
[![codecov](https://codecov.io/gh/NeoSmartpen/hwr-api/branch/master/graph/badge.svg?token=XZrGJ6Hjyd)](https://codecov.io/gh/NeoSmartpen/hwr-api)
[![Maintainability](https://api.codeclimate.com/v1/badges/f9d3abeff7cd2837dc1f/maintainability)](https://codeclimate.com/repos/63adb7bad57e9700c30096e4/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/f9d3abeff7cd2837dc1f/test_coverage)](https://codeclimate.com/repos/63adb7bad57e9700c30096e4/test_coverage)


[![DeepSource](https://deepsource.io/gh/NeoSmartpen/hwr-api.svg/?label=active+issues&show_trend=true&token=8xmxsoemP2Ybzq2ol_XDOuMo)](https://deepsource.io/gh/NeoSmartpen/hwr-api/?ref=repository-badge)

### Usage

```yaml
      - name: Pull-Request-Typography
        uses: chyccs/pull-request-typography@master
        continue-on-error: true
        with:
          src_path: "."
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
