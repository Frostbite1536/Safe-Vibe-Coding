source "https://rubygems.org"

# Jekyll version compatible with GitHub Pages
gem "jekyll", "~> 3.9.3"

# GitHub Pages gem includes Jekyll and common plugins
gem "github-pages", "~> 228", group: :jekyll_plugins

# Plugins used by this site
group :jekyll_plugins do
  gem "jekyll-seo-tag"
  gem "jekyll-github-metadata"
  gem "jekyll-include-cache"
end

# Windows and JRuby does not include zoneinfo files
platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end

# Performance-booster for watching directories on Windows
gem "wdm", "~> 0.1", :platforms => [:mingw, :x64_mingw, :mswin]

# Lock `http_parser.rb` gem to `v0.6.x` on JRuby builds
gem "http_parser.rb", "~> 0.6.0", :platforms => [:jruby]
