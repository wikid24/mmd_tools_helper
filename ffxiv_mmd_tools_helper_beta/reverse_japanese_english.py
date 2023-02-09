import bpy

from . import register_wrap

"""
@register_wrap
class ReverseJapaneseEnglishPanel(bpy.types.Panel):
	#Sets up nodes in Blender node editor for rendering toon textures
	bl_idname = "OBJECT_PT_reverse_japanese_english"
	bl_label = "Reverse Japanese English names"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS" if bpy.app.version < (2,80,0) else "UI"
	bl_category = "ffxiv_mmd_tools_helper"

	def draw(self, context):
		layout = self.layout
		row = layout.row()

		row.label(text="Reverse Japanese English names", icon="TEXT")
		row = layout.row()
		row.operator("ffxiv_mmd_tools_helper.reverse_japanese_english", text = "Reverse Japanese English names")
		row = layout.row()
"""

def swap_japanese_english(context):
	for m in bpy.data.materials:
		name_j = m.mmd_material.name_j
		name_e = m.mmd_material.name_e
		if name_e != '':
			m.mmd_material.name_e = name_j
			m.mmd_material.name_j = name_e
			m.mmd_material.name = name_e

	for m in bpy.data.materials:
		m.name = m.mmd_material.name


	for o in bpy.context.view_layer.objects:
		if o.type == 'ARMATURE':
			o.data.show_names = True
			bpy.context.view_layer.objects.active = o
			bpy.ops.object.mode_set(mode='POSE')
			for b in bpy.context.active_object.pose.bones:
				name_j = b.mmd_bone.name_j
				name_e = b.mmd_bone.name_e
				if name_e != '':
					b.mmd_bone.name_j = name_e
					b.mmd_bone.name_e = name_j
					b.name = name_e

	bpy.ops.object.mode_set(mode='OBJECT')

	for o in bpy.context.view_layer.objects:
		if o.mmd_type == 'ROOT':
			for vm in o.mmd_root.vertex_morphs:
				name_j = vm.name
				name_e = vm.name_e
				if name_e != '':
					vm.name = name_e
					vm.name_e = name_j


@register_wrap
class ReverseJapaneseEnglish(bpy.types.Operator):
	"""Reverses Japanese and English names of shape keys, materials, bones"""
	bl_idname = "ffxiv_mmd_tools_helper.reverse_japanese_english"
	bl_label = "Reverse Japanese English names of MMD model"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		swap_japanese_english(context)
		return {'FINISHED'}