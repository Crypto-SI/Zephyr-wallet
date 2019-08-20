# macOS Tor Proxy setup

To install Tor Proxy on macOS using [homebrew](https://brew.sh/)
package manager first install homebrew:

```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Then install Tor Proxy:

```
brew install tor

brew services start tor
```
