/* File Icons Builder
 * -------------------------------------------------------------------------- *
 * Developed with love & patience by Ihor Oleksandrov
 * -------------------------------------------------------------------------- */

'use strict';

/*
 * > Plugins
 */

var gulp = require('gulp');
var color = require('color');
var colors = require('colors');
var path = require('path');
var conventionalChangelog = require('conventional-changelog');
var conventionalGithubReleaser = require('conventional-github-releaser');
var argv = require('yargs').argv;
var fs = require('fs');
var merge = require('merge-stream');
var $ = require('gulp-load-plugins')();

/*
 * > Options
 */

var opts = {};

opts.colors = require('./src/colors.json');
opts.sizes = require('./src/sizes.json');
opts.envRegEx = new RegExp('([\'|\"]?__version__[\'|\"]?[ ]*[:|=][ ]*[\'|\"]?)(\\d+\\.\\d+\\.\\d+)(-[0-9A-Za-z\.-]+)?([\'|\"]?)', 'i');


/*
 * > Helpers
 */

var getIconOpts = function() {
  return JSON.parse(fs.readFileSync('./src/icons.json', 'utf8'));
};

var getIconScope = function(iconOpts) {
  var syntaxes = iconOpts.syntaxes;
  var aliases = iconOpts.aliases;

  var scope = '';

  if (syntaxes) {
    for (var syntax in syntaxes) {
      scope = scope + syntaxes[syntax].scope + ', ';
    }
  }

  if (aliases) {
    for (var alias in aliases) {
      scope = scope + aliases[alias].scope + ', ';
    }
  }

  return scope.slice(0, -2);
};

/*
 * > Build
 */

gulp.task('build', ['build:settings', 'build:icons']);

// >> Settings

gulp.task('build:settings', function() {
  opts.icons = getIconOpts();

  return gulp.src('./src/assets/*.svg', {read: false})
    .pipe($.plumber(function(error) {
      console.log('[build:settings]'.bold.magenta + ' There was an issue building icon settings:\n'.bold.red + error.message);
      this.emit('end');
    }))
    .pipe($.flatmap(function(stream, file) {
      var iconName = path.basename(file.path, path.extname(file.path));
      var iconOpts = opts.icons[iconName];
      var iconScope = getIconScope(iconOpts);
      var iconAliases = iconOpts.aliases;
      var iconSettings = merge();

      if (iconScope) {
        iconSettings.add(gulp.src('./src/templates/preference.xml')
          .pipe($.data(function() {
            return {
              name: iconName,
              scope: iconScope
            };
          }))
          .pipe($.template())
          .pipe($.rename({
            basename: iconName,
            extname: '.tmPreferences'
          }))
          .pipe(gulp.dest('./dist/preferences'))
        );
      }

      if (iconAliases) {
        iconSettings.add(iconAliases.map(function(alias) {
          return gulp.src('./src/templates/language.xml')
            .pipe($.data(function() {
              return {
                alias: alias.name,
                extensions: alias.extensions,
                base: alias.base,
                scope: alias.scope
              };
            }))
            .pipe($.template())
            .pipe($.rename({
              basename: alias.name,
              extname: '.tmLanguage'
            }))
            .pipe(gulp.dest('./dist/languages'));
        }));
      }

      return iconSettings.isEmpty() ? stream : iconSettings;
    }));
});

// >> Icons

gulp.task('build:icons', function() {
  var baseColor = $.recolorSvg.ColorMatcher(color('#000'));

  opts.icons = getIconOpts();

  return gulp.src('./src/assets/*.svg')
    .pipe($.plumber(function(error) {
      console.log('[build:icons]'.bold.magenta + ' There was an issue rasterizing icons:\n'.bold.red + error.message);
      this.emit('end');
    }))
    .pipe($.changed('./dist/zpatches/icons', {extension: '.png'}))
    .pipe($.flatmap(function(stream, file) {
      var iconName = path.basename(file.path, path.extname(file.path));
      var iconOpts = opts.icons[iconName];
      var iconColor = color(opts.colors[iconOpts.color]);

      var iconImages = merge();

      iconImages.add(opts.sizes.map(function(size) {
        var multi = gulp.src(file.path)
          .pipe($.recolorSvg.Replace(
            [baseColor],
            [iconColor]
          ))
          .pipe($.svg2png({
            width: size.size,
            height: size.size
          }))
          .pipe($.if(size.size, $.rename({suffix: size.suffix})))
          .pipe($.imagemin([$.imagemin.optipng({
            bitDepthReduction: false,
            colorTypeReduction: false,
            paletteReduction: false
          })], {verbose: true}))
          .pipe(gulp.dest('./dist/zpatches/icons'));

        var single = gulp.src(file.path)
          .pipe($.recolorSvg.Replace(
            [baseColor],
            [color('white')]
          ))
          .pipe($.svg2png({
            width: size.size,
            height: size.size
          }))
          .pipe($.if(size.size, $.rename({suffix: size.suffix})))
          .pipe($.imagemin([$.imagemin.optipng({
            bitDepthReduction: false,
            colorTypeReduction: false,
            paletteReduction: false
          })], {verbose: true}))
          .pipe(gulp.dest('./dist/zpatches/single'));

        return merge(multi, single);
      }));

      return iconImages;
    }));
});

/*
 * > Release
 */

gulp.task('media', function() {
  return gulp.src('./media/*.png')
    .pipe($.imagemin({verbose: true}))
    .pipe(gulp.dest('./media'));
});

gulp.task('changelog', function() {
  return conventionalChangelog({
    preset: 'angular',
    releaseCount: 0
  })
  .pipe(fs.createWriteStream('CHANGELOG.md'));
});

gulp.task('bump-version', ['bump-pkg-version', 'bump-env-version']);

gulp.task('bump-pkg-version', function() {
  return gulp.src('./package.json')
    .pipe($.if(argv.patch, $.bump()))
    .pipe($.if(argv.minor, $.bump({ type: 'minor' })))
    .pipe($.if(argv.major, $.bump({ type: 'major' })))
    .pipe(gulp.dest('./'));
});

gulp.task('bump-env-version', function() {
  return gulp.src('./util/env.py')
    .pipe($.if(argv.patch, $.bump({ regex: opts.envRegEx })))
    .pipe($.if(argv.minor, $.bump({ type: 'minor', regex: opts.envRegEx })))
    .pipe($.if(argv.major, $.bump({ type: 'major', regex: opts.envRegEx })))
    .pipe(gulp.dest('./util'));
});

gulp.task('github-release', function(done) {
  conventionalGithubReleaser({
    type: 'oauth',
    token: process.env.CONVENTIONAL_GITHUB_RELEASER_TOKEN
  }, {
    preset: 'angular'
  }, done);
});

/*
 * > Watch
 */

gulp.task('watch', function() {
  $.watch('./src/assets/*.svg', $.batch(function(events, done) {
    gulp.start('build', done);
  }));

  $.watch('./src/*.json', $.batch(function(events, done) {
    gulp.start('build:settings', done);
  }));
});

/*
 * > Default
 */

gulp.task('default', ['build']);
