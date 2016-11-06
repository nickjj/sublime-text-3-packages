# -*- coding: utf-8 -*-

PATCH_TEMPLATE = '''
// %(name)s Theme Overlay
// ============================================================================

[
  // Sidebar File Icons
  // --------------------------------------------------------------------------

  // Default

  {
    "class": "icon_file_type",%(color)s
    "layer0.opacity": %(opacity)s,
    "content_margin": [%(size)s, %(size)s]
  },

  // Hovered

  {
    "class": "icon_file_type",%(color_on_hover)s
    "parents": [{"class": "tree_row", "attributes": ["hover"]}],
    "layer0.opacity": %(opacity_on_hover)s
  },

  // Selected

  {
    "class": "icon_file_type",%(color_on_select)s
    "parents": [{"class": "tree_row", "attributes": ["selected"]}],
    "layer0.opacity": %(opacity_on_select)s
  }
]
'''
