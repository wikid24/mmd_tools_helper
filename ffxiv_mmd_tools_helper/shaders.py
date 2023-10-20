import bpy
import os
from . import register_wrap
from struct import unpack, pack
from os.path import isfile

def read_i(file, i):
	return [unpack('e', file.read(2))[0] for x in range(i)]

def apply_colorset_file(file_name):
	for obj in bpy.context.selected_objects:
		if obj.type =='MESH' and obj.active_material.is_colorset:
			colorsetdat = False
			if isfile(file_name[:-3]+'dat'):
				colorsetdat = open(file_name[:-3]+'dat', 'rb')
			with open(file_name, 'rb') as colorset:
				colorset.seek(128)
				for i in range(16):
					bpy.context.object.active_material.cs_rows[i].diff = read_i(colorset, 4)
					# these properties have to be 4 long to update properly, 4th is dummy,
					# won't append directly to the read_i call for some reason...
					spec = read_i(colorset, 3)
					spec.append(1.0)
					bpy.context.object.active_material.cs_rows[i].spec = spec
					bpy.context.object.active_material.cs_rows[i].gloss = read_i(colorset, 1)[0]
					glow = read_i(colorset, 3)
					glow.append(1.0)
					bpy.context.object.active_material.cs_rows[i].glow = glow
					bpy.context.object.active_material.cs_rows[i].tile_id = int(read_i(colorset, 1)[0] * 64)
					bpy.context.object.active_material.cs_rows[i].tile_transform = [x for x in read_i(colorset, 4)]
					if colorsetdat:
						bpy.context.object.active_material.cs_rows[i].dye = hex(unpack('>H', colorsetdat.read(2))[0])[2:]

				colorset.close()
			if colorsetdat:
				colorsetdat.close()

def apply_multimap_file(multimap_file):
	for obj in bpy.context.selected_objects:
		if obj.type =='MESH' and obj.active_material.is_colorset:
			for slot in obj.material_slots:
					mat = slot.material

					for node in mat.node_tree.nodes:
						if node.label =='MultiTexture':
							node.image = multimap_file


def apply_normalmap_file(normalmap_file):
	for obj in bpy.context.selected_objects:
		if obj.type =='MESH' and obj.active_material.is_colorset:
			for slot in obj.material_slots:
					mat = slot.material
					
					for node in mat.node_tree.nodes:
						if node.label =='Normal Texture':
							node.image = normalmap_file
							fix_normalmap()

def apply_specular_file(specular_file):
	for obj in bpy.context.selected_objects:
		if obj.type =='MESH' and obj.active_material.is_colorset:
			for slot in obj.material_slots:
					mat = slot.material
					
					for node in mat.node_tree.nodes:
						if node.label =='Specular Texture':
							node.image = specular_file

def apply_diffuse_file(diffuse_file):
	for obj in bpy.context.selected_objects:
		if obj.type =='MESH' and obj.active_material.is_colorset:
			for slot in obj.material_slots:
					mat = slot.material
					
					for node in mat.node_tree.nodes:
						if node.label =='Diffuse Texture':
							node.image = diffuse_file							
							
							


def fix_normalmap ():
	for obj in bpy.context.selected_objects:
		if obj.type =='MESH' and obj.active_material.is_colorset:    
			for slot in obj.material_slots:
				mat = slot.material
				
				#print (f"The material in slot {slot.name} of object {obj.name} is {mat.name}")
				
				normal_texture_node = None
				
				
				#set the 'Normal Texture' node's Colorspace to Non-Colour
				for node in mat.node_tree.nodes:
					#print (f"Name: {node.name}, Label: {node.label}")
					if node.label =='Normal Texture':
						normal_texture_node = node
						if node.image:
							node.image.colorspace_settings.name = 'Non-Color'
				#set the 'Normal Texture (Closest)' node's to the same image as 'Normal Texture'
				if normal_texture_node:
					for node in mat.node_tree.nodes:
						#print (f"Name: {node.name}, Label: {node.label}")
						if node.label =='Normal Texture (Closest)':
							node.image = normal_texture_node.image

def fix_material_output_node():
	#if "Principled BSDF" node output BSDF is not connected to "Material Output" node Surface input, then connect them
	if bpy.context.active_object:
		obj = bpy.context.active_object
		if obj.type =='MESH' and obj.active_material.is_colorset:
			
			mat = obj.active_material

			principled_bsdf = None
			material_output = None
			
			for node in mat.node_tree.nodes:
				if node.name =='Principled BSDF':
					principled_bsdf = node
					#print (principled_bsdf)

				if node.name =='Material Output':
					material_output = node
					#print (material_output)

				#mat.node_tree.links.new(material_output.inputs['Surface'], principled_bsdf.outputs['BSDF'])
				#bpy.context.selected_objects[0].active_material.node_tree.links.new(material_output.inputs['Surface'],principled_bsdf.outputs['BSDF'])
				if principled_bsdf and material_output:
					mat.node_tree.links.new(material_output.inputs['Surface'],principled_bsdf.outputs['BSDF'])
				#if principled_bsdf.output

def apply_colorset_plugin():
	if bpy.context.active_object:
			obj = bpy.context.active_object

			if obj.type =='MESH':
				if not obj.active_material.is_colorset:
					bpy.ops.object.add_cs_material()


def apply_glossy_shader():
    active_object = bpy.context.active_object
    if active_object and active_object.active_material:
        active_material = active_object.active_material
        if active_material.node_tree:
            for node in active_material.node_tree.nodes:
                if node.name == 'Material Output':
                    material_output = active_material.node_tree.nodes['Material Output']
                    
                    #get main shader from Material Output
                    if not material_output.inputs[0].links[0].from_node.name=='Mix Shader':
                        main_shader = material_output.inputs[0].links[0].from_node
                    else:
                        mix_shader = active_material.node_tree.nodes['Mix Shader']
                        main_shader = mix_shader.inputs[1].links[0].from_node
                    
                    
                    # Add a Mix Shader node
                    mix_shader = None
                    if 'Mix Shader' in active_material.node_tree.nodes:
                        mix_shader = active_material.node_tree.nodes['Mix Shader']
                    else:
                        mix_shader = active_material.node_tree.nodes.new(type='ShaderNodeMixShader')
                        mix_shader.location = material_output.location
                        mix_shader.location.x = mix_shader.location.x - 200
                    
                    #connect Mix Shader to Material Output    
                    active_material.node_tree.links.new(mix_shader.outputs[0], material_output.inputs[0])

                    # Connect Main Shader to Mix Shader
                    active_material.node_tree.links.new(main_shader.outputs[0], mix_shader.inputs[1])
                    
                    
                    # Add a Glossy BSDF node
                    glossy_bsdf = None
                    if 'Glossy BSDF' in active_material.node_tree.nodes:
                        glossy_bsdf = active_material.node_tree.nodes['Glossy BSDF']
                    else:
                        glossy_bsdf = active_material.node_tree.nodes.new(type='ShaderNodeBsdfGlossy')
                        glossy_bsdf.location = mix_shader.location
                        glossy_bsdf.location.y = glossy_bsdf.location.y - 400
                        
                    #connect glossy bsdf to mix shader node
                    active_material.node_tree.links.new(glossy_bsdf.outputs[0], mix_shader.inputs[2])
                    
                    #get node connected from main_shader 'Base Color'
                    if main_shader.name == 'Principled BSDF':
                        diffuse_node = main_shader.inputs[0].links[0].from_node
                    if main_shader.name == 'mmd_shader':
                        diffuse_node = main_shader.inputs['Base Tex'].links[0].from_node
                            
                    # Connect diffuse_node to Glossy BSDF
                    active_material.node_tree.links.new(diffuse_node.outputs['Color'], glossy_bsdf.inputs[0]) 
                    
                    #get node connected from Principled BSDF 'Normal'
                    if main_shader.name == 'Principled BSDF':
                        normalmap_node = main_shader.inputs['Normal'].links[0].from_node
                    else:
                        normalmap_node = active_material.node_tree.nodes['Normal Map']
                    
                    #connect normalmap_node to Glossy BSDF
                    active_material.node_tree.links.new(normalmap_node.outputs[0], glossy_bsdf.inputs[2]) 
                

@register_wrap
class ApplyGLossyShader(bpy.types.Operator):
	"""User can select the folder for materials"""
	bl_idname = "ffxiv_mmd.apply_glossy_shader"
	bl_label = "Add Glossy Shader to Material"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.type == 'MESH'

	def execute(self, context):
		apply_glossy_shader()
		return {'FINISHED'}


@register_wrap
class SelectMaterialsFolder(bpy.types.Operator):
	"""User can select the folder for materials"""
	bl_idname = "ffxiv_mmd.select_materials_folder"
	bl_label = "Select Materials Folder"
	bl_options = {'REGISTER', 'UNDO'}

	#folder_path = "yoooooo"
	bpy.types.Scene.shaders_texture_folder = bpy.props.StringProperty(name="Texture Folder", description="Folder where the gear for _a, _m, and _n files are located", default="", maxlen=0, options={'ANIMATABLE'}, subtype='DIR_PATH', update=None, get=None, set=None)

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.type == 'MESH'

	def execute(self, context):
		folder_path = context.scene.shaders_texture_folder
		#context.scene.ffxiv_mmd.select_materials_folder.folder_path
		
		apply_colorset_plugin()

		#print (context.scene.shaders_texture_folder)
		if bpy.context.active_object:
			obj = bpy.context.active_object

			if obj.type =='MESH' and obj.active_material.is_colorset :

				colorset_files = [f for f in os.listdir(context.scene.shaders_texture_folder) if f.endswith('_a.dds') ]
				multimap_files = [f for f in os.listdir(context.scene.shaders_texture_folder) if f.endswith('_m.bmp') or f.endswith('_m.png')]
				normalmap_files = [f for f in os.listdir(context.scene.shaders_texture_folder) if f.endswith('_n.bmp') or f.endswith('_n.png')]
				specular_files = [f for f in os.listdir(context.scene.shaders_texture_folder) if f.endswith('_s.bmp') or f.endswith('_s.png')]
				diffuse_files = [f for f in os.listdir(context.scene.shaders_texture_folder) if f.endswith('_d.bmp') or f.endswith('_d.png')]
				colorset_filename = None
				multimap_filename = None
				normalmap_filename = None
				specular_filename = None


				if colorset_files:
					colorset_filename = folder_path+colorset_files[0]
					#print(f"Colorset file found: {colorset_filename}")
					apply_colorset_file(colorset_filename)
				else:
					print("No colorset file ending with '_a' found in the folder.")
						
						
				if multimap_files:
					multimap_filename = folder_path+multimap_files[0]
					# Specify the name of the image you want to check
					if multimap_files[0] not in bpy.data.images:
						multimap = bpy.data.images.load(multimap_filename)
						
					else:
						multimap = bpy.data.images[multimap_files[0]]
						print(f"Multimap file found: {multimap_filename}")
						print(f"Multimap: {multimap}")
					apply_multimap_file(multimap)
				else:
					print("No multimap file ending with '_m' found in the folder.")
					
						
				if normalmap_files:
					normalmap_filename = folder_path+normalmap_files[0]
					if normalmap_files[0] not in bpy.data.images:
						normalmap = bpy.data.images.load(normalmap_filename)
					
					else:
						normalmap = bpy.data.images[normalmap_files[0]]
					#print(f"Normalmap file found: {normalmap_filename}")
					apply_normalmap_file(normalmap)
				else:
					print("No normalmap file ending with '_n' found in the folder.")

				if specular_files:
					specular_filename = folder_path+specular_files[0]
					if specular_files[0] not in bpy.data.images:
						specular = bpy.data.images.load(specular_filename)
						#apply_normalmap_file(normalmap)
					else:
						specular = bpy.data.images[specular_files[0]]
					#print(f"Specular file found: {normalmap_filename}")
					apply_specular_file(specular)
				else:
					print("No specular file ending with '_s' found in the folder.")


				if diffuse_files:
					diffuse_filename = folder_path+diffuse_files[0]
					if diffuse_files[0] not in bpy.data.images:
						diffuse = bpy.data.images.load(diffuse_filename)
						#apply_normalmap_file(normalmap)
					else:
						diffuse = bpy.data.images[diffuse_files[0]]
					#print(f"Diffuse file found: {normalmap_filename}")
					apply_diffuse_file(diffuse)
				else:
					print("No diffuse file ending with '_d' found in the folder.")						
					
				#if colorset_filename and multimap_filename and normalmap_filename:
					
					
					


				fix_material_output_node()

				#print(f"Selected folder: {folder_path}")
				return {'FINISHED'}
	

@register_wrap
class FixNormalMaps(bpy.types.Operator):
	"""User can select the folder for materials"""
	bl_idname = "ffxiv_mmd.fix_normal_maps"
	bl_label = "Fix the Normal Maps"
	bl_options = {'REGISTER', 'UNDO'}



	def main (context):
		fix_normalmap()


	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		FixNormalMaps.main(context)
		return {'FINISHED'}