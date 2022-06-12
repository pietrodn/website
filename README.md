# Pietro's website

This is the source code of my personal website, online at https://blog.pietrodn.com.

It is automatically built and deployed by a GitHub Actions workflow.


## Installation

```
git clone git@github.com:pietrodn/website.git
cd website
git submodule init
git submodule update
```

## Production build

```
hugo --minify
```

## Development / writing

Starts a live website that refreshes at every update.
```
hugo server
```
