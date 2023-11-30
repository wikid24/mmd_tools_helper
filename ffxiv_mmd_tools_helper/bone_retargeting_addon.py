import bpy
import addon_utils
from . import register_wrap
from . import bone_tools

"""
import sys
from pathlib import Path

addon_name = "blender-animation-retargeting-stable"
# Get the addon's path
addon_path = Path(bpy.utils.user_resource('SCRIPTS')).joinpath('addons', addon_name)
# Add the addon's path to sys.path temporarily
sys.path.append(str(addon_path))
# Now you can import modules from the addon
from mapping import *
# Remove the addon's path from sys.path to avoid conflicts
sys.path.remove(str(addon_path))
"""

####################### INFO ###############################

#enter bone mapping mode
#bpy.ops.mappings.edit()

#adds a row
#bpy.ops.mappings.list_action(action="ADD")
#removes a row
#bpy.ops.mappings.list_action(action="REMOVE")

#source_armature
#bpy.context.object['retargeting_context']['source']

#target_armature
#bpy.context.object['retargeting_context']['target']


#data_rows
#bpy.context.object['retargeting_context']['mappings'][0]['source']
#bpy.context.object['retargeting_context']['mappings'][0]['target']

######################################################

def is_addon_installed():
	addon_name = 'blender-animation-retargeting-stable'
	addon_required_version = (2,1,0)
	addon_module = None
	try:
		addon_module = [m for m in addon_utils.modules() if m.__name__ == addon_name][0] # get module
	except:
		return False
		#raise Exception(f"The addon {addon_name} is not installed or is not enabled. Please install and enable it.")

	if addon_module:
		installed_version = addon_module.bl_info.get('version',(-1,-1,-1))

	# Check if the addon is enabled
	if addon_name not in bpy.context.preferences.addons.keys():
		return False
		#raise Exception(f"The addon '{addon_name}' is not installed or is not enabled. Please install and enable it.")
	elif  installed_version < addon_required_version:
		return False
		#raise Exception(f"Addon '{addon_name}' version is {installed_version} please install {addon_required_version} or higher.")
	else:
		return True
		#print(f"The addon '{addon_name}' is installed and enabled.")

def is_source_and_target_mapped(armature):
	source_arm = armature.get('retargeting_context').get('source')
	target_arm = armature.get('retargeting_context').get('target')
	if source_arm and target_arm:
		return True
	else:
		return False

def compare_str(string1,string2):
	if string1 and string2:
		cleaned_string1 = string1.strip().lower()
		cleaned_string2 = string2.strip().lower()

		return cleaned_string1 == cleaned_string2
	else:
		return False

def add_bone_mapping(target_armature, source_bone,target_bone):


	#print(f"source_armature:{source_bone.id_data.name}, source_bone:{source_bone.name}, target_armature:{target_armature.name}, target_bone:{target_bone.name}")	

	if source_bone and target_bone:

		# THERE IS A DIFFERENCE BETWEEN active_object.retargeting_context and active_object.get('retargeting_context')
		rtc = target_armature.get('retargeting_context') #THIS IS A PROPERTY GROUP FOR USING .get('source')/.get('target')/.get('mappings') TO GET DATA
		art_mapping_controls = bpy.context.active_object.retargeting_context #THIS IS OPERATOR CONTROLS FOR WHAT IS SEEN ON THE VIEWPORT SOMETIMES IT IS WRONG
		art_mapping_controls.ui_editing_mappings = True

		#get mapping list
		read_only_mapping_data = rtc.get('mappings') #THIS RETURNS A VIEWABLE LIST but you can't edit it YOU NEED ART_MAPPING_CONTROLS FOR THIS

		if read_only_mapping_data is None or len(read_only_mapping_data) == 0:
				#bpy.ops.mappings.list_action(action="ADD")
				#needed because mappings won't exist until at least one thing is added
				art_mapping_controls.mappings.add()
				art_mapping_controls.active_mapping = 0
		
		#THIS CODE IS HERE BECAUSE THIS FUNCTION IS CURSED
		read_only_mapping_data = rtc.get('mappings')

		if read_only_mapping_data:

			if len(read_only_mapping_data) == 1 and art_mapping_controls.mappings[0].get('source') is None and art_mapping_controls.mappings[0].get('target') is None:
				art_mapping_controls.mappings[0]['source'] = source_bone.name
				art_mapping_controls.mappings[0]['target'] = target_bone.name
			
			else:
				mapping_found = False	
				art_mapping_controls.active_mapping = 0
				#loop through all the mappings and see if there is an existing mapping
				for i,mapping in enumerate(read_only_mapping_data):
					source_bone_mapping = mapping.get('source')
					target_bone_mapping = mapping.get('target')
					art_mapping_controls.active_mapping = i

					if compare_str(source_bone_mapping,source_bone.name) and compare_str(target_bone_mapping,target_bone.name):
						mapping_found = True
						
					#check if source bone is mapped to a different target bone, and remove the source bone from mapping
					elif compare_str(source_bone_mapping,source_bone.name) and not(compare_str(target_bone_mapping,target_bone.name)):
						art_mapping_controls.mappings[i]['source'] = ''

					#check if target bone is mapped to a different source bone, and remove the target bone mapping
					elif compare_str(target_bone_mapping,target_bone.name) and not(compare_str(source_bone_mapping,source_bone.name)):
						art_mapping_controls.mappings[i]['target'] = ''		
				
				if mapping_found == False:
					mapping = art_mapping_controls.mappings.add()
					mapping['source'] = source_bone.name
					mapping['target'] = target_bone.name
					art_mapping_controls.active_mapping = len(read_only_mapping_data)

			
			# Garbage cleanup, iterating backward
			for i,mapping in enumerate(read_only_mapping_data):
				art_mapping_controls.active_mapping = i

				if (art_mapping_controls.mappings[i].get('source') is None or art_mapping_controls.mappings[i].get('source') =='') \
					or (art_mapping_controls.mappings[i].get('target') is None or art_mapping_controls.mappings[i].get('target') ==''):
					art_mapping_controls.mappings.remove(i)

			#bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
	
	bpy.context.view_layer.update()

	return

def remove_bone_mapping(source_bone_name,target_bone_name):

	rtc = bpy.context.object.get('retargeting_context')
	mapping_list = rtc.get('mappings')
	active_mapping = rtc.get('active_mapping')
	for i,mapping in enumerate(mapping_list):
		active_mapping = i
		source_bone_mapping = mapping.get('source')
		target_bone_mapping = mapping.get('target')

		if (source_bone_mapping == source_bone_name) and (target_bone_mapping == target_bone_name):
			bpy.ops.mappings.list_action(action="REMOVE")
			active_mapping = i-1

	
	#check if exists on the bone mapping


	#remove
	

	return

def get_mapping_bone_group_list(bone_group):

	bone_group_dictionary = ['all_verbatim','body','breast','eye','eyelid','eyebrow','nose','mouth','ear','skirt']

	if bone_group in bone_group_dictionary:
		#get ALL bones names from ALL target_columns where animation_retargeting_group is not blank
		target_columns = ['mmd_english', 'mmd_japanese', 'mmd_japaneseLR', 'blender_rigify', 'ffxiv','mmd_kaito']
		FFXIV_BONE_METADATA_DICTIONARY = bone_tools.get_csv_metadata_by_bone_type('animation_retargeting_group', target_columns)

	bone_list = []

	if FFXIV_BONE_METADATA_DICTIONARY is not None:

		#run through the bone dictionary and only append bones that match bone_group
		for metadata_bone in FFXIV_BONE_METADATA_DICTIONARY:
			if metadata_bone[0] == bone_group:
				bone_list.append(metadata_bone[1])
				#print(metadata_bone[1])

		return bone_list
	
	return None

def get_mapping_target_bones(bone_group,target_armature):

	#get ALL bones that match the bone group
	all_bones_in_bone_group = get_mapping_bone_group_list(bone_group)

	#run through all the bones and append it to bone_list if it exists on the target armature
	if all_bones_in_bone_group:

		bone_list = []

		for bone_name in all_bones_in_bone_group:
			target_bone = target_armature.pose.bones.get(bone_name)

			if target_bone:
				bone_list.append(target_bone)

		if bone_list is not None:
			return bone_list
		
	return None



@register_wrap
class ART_AddBoneMapping(bpy.types.Operator):
	"""Adds a bone mapping"""
	bl_idname = "ffxiv_mmd.art_add_bone_mapping"
	bl_label = "Applies Bone Rotation to Target Bone Group"
	bl_options = {'REGISTER', 'UNDO'}

	#reference data only
	bone_group_list = ['all_verbatim','body','breast','eye','eyelid','eyebrow','nose','mouth','ear','skirt','clear_mapping']

	bone_group = bpy.props.StringProperty(name="bone_group", update=None, get=None, set=None)

	def execute(self, context):

		if is_addon_installed():
			active_object = context.active_object
			# THERE IS A DIFFERENCE BETWEEN active_object.retargeting_context and active_object.get('retargeting_context')
			rtc = active_object.get('retargeting_context')

			source_arm = rtc.get('source')
			target_arm = rtc.get('target')

			if is_source_and_target_mapped(active_object):

				if self.bone_group=='clear_mapping':
					active_object.retargeting_context.reset()

				elif self.bone_group =='all_verbatim':
					for target_bone in target_arm.pose.bones:
						source_bone = None

						source_bone = source_arm.pose.bones.get(target_bone.name)

						if not(source_bone):
							source_bone = bone_tools.get_equivalent_bone_from_armature(target_arm,target_bone,source_arm)

						if source_bone and target_bone:
							add_bone_mapping(target_arm, source_bone,target_bone)
				else:

					target_bone_list = get_mapping_target_bones(self.bone_group,target_arm)					

					if target_bone_list:

						#loop through all the target bones and see if it exists on the source armature
						for target_bone in target_bone_list:
							source_bone = bone_tools.get_equivalent_bone_from_armature(target_arm,target_bone,source_arm)	
							if source_bone and target_bone:
								add_bone_mapping(target_arm, source_bone,target_bone)


				##############ADD SPECIAL CODE FOR MMD KAITO MODEL BECAUSE IT USES DIFFERENT THUMB BONES
				if self.bone_group in ('body','all_verbatim'):
					has_all_kaito_bones = True
					mmd_kaito_bones = ('親指０.L','親指１.L','親指０.R','親指１.R')
					#mmd_e_bones = ('thumb1_L','thumb2_L','thumb1_R','thumb2_R')

					for bone_name in mmd_kaito_bones:
						print(bone_name)
						if bone_name not in source_arm.pose.bones:
							print('its not in it')
							has_all_kaito_bones = False
						else:
							print('its in it')

					print('has all kaito bones:', has_all_kaito_bones)

					if has_all_kaito_bones:
						for kaito_bone_name in mmd_kaito_bones: 
							kaito_bone_mmd_e = bone_tools.get_mmd_english_equivalent_bone_name(kaito_bone_name,'mmd_kaito')
							source_bone_name = bone_tools.get_armature_bone_name_by_mmd_english_bone_name(source_arm,kaito_bone_mmd_e)
							source_bone = source_arm.pose.bones.get(source_bone_name)

							target_bone = bone_tools.get_equivalent_bone_from_armature(source_arm,source_bone,target_arm)
							print(f'source bone {source_bone.name} target bone {target_bone.name}')
							add_bone_mapping(target_arm,source_bone,target_bone)

				#######################################################################################

							
					
		return {'FINISHED'}


def get_rotate_bone_group_list(bone_group):

	if bone_group == 'upperarm':
		return ['arm_L','arm_R']
	if bone_group == 'forearm':
		return ['elbow_L','elbow_R']
	if bone_group == 'wrist':
		return ['wrist_L','wrist_R']
	if bone_group == 'hand':
		return ['thumb1_L','thumb2_L','fore1_L','fore2_L','fore3_L','middle1_L','middle2_L','middle3_L','third1_L','third2_L','third3_L','little1_L','little2_L','little3_L',
				'thumb1_R','thumb2_R','fore1_R','fore2_R','fore3_R','middle1_R','middle2_R','middle3_R','third1_R','third2_R','third3_R','little1_R','little2_R','little3_R']
	if bone_group == 'upperleg':
		return ['leg_L','leg_R']
	if bone_group == 'lowerleg':
		return ['knee_L','knee_R','knee_2_L','knee_2_R']
	if bone_group == 'feet':
		return ['ankle_L','ankle_R']
	if bone_group == 'toe':
		return ['toe_L','toe_R']
	
	
	return False
	

@register_wrap
class ART_ApplyBoneRotationToTarget(bpy.types.Operator):
	"""Applies Bone Rotation to Target Bone Group"""
	bl_idname = "ffxiv_mmd.art_apply_bone_rotation_to_target"
	bl_label = "Applies Bone Rotation to Target Bone Group"
	bl_options = {'REGISTER', 'UNDO'}

	#reference data only, this isn't used anywhere
	bone_group_list = ['upperarm','forearm','wrist','hand','upperleg','lowerleg','feet','toe','clear_mapping_source','clear_mapping_target']

	bone_group = bpy.props.StringProperty(name="bone_group", update=None, get=None, set=None)

	bpy.types.Scene.art_reset_rot_if_no_match = bpy.props.BoolProperty(name="art_reset_rot_if_no_match", default=False)

	def execute(self, context):
		
		active_object = context.active_object
		rtc = active_object.get('retargeting_context')
		source_arm = rtc.get('source')
		target_arm = rtc.get('target')

		print(source_arm)
		print(target_arm)

		if self.bone_group == 'clear_mapping_source':
			for pose_bone in source_arm.pose.bones:
				bone_tools.clear_rotation(pose_bone)
				bone_tools.clear_location(pose_bone)

		
		elif self.bone_group == 'clear_mapping_target':
			for pose_bone in target_arm.pose.bones:
				bone_tools.clear_rotation(pose_bone)
				bone_tools.clear_location(pose_bone)

		elif is_source_and_target_mapped(active_object):
			
			bone_list_mmd_english = get_rotate_bone_group_list(self.bone_group)
			
			if bone_list_mmd_english:

				# Find and store the handle_edit_change function
				stored_handler = None
				for handler in bpy.app.handlers.depsgraph_update_post:
					if '<function handle_edit_change' in str(handler):
						stored_handler = handler.copy
						break

				# Remove the stored function from the handler list
				if stored_handler:
					bpy.app.handlers.depsgraph_update_post.remove(stored_handler)

				for bone in bone_list_mmd_english:
					source_bone_name = bone_tools.get_armature_bone_name_by_mmd_english_bone_name(source_arm,bone)
					target_bone_name = bone_tools.get_armature_bone_name_by_mmd_english_bone_name(target_arm,bone)
					source_bone = None
					target_bone = None
					
					if target_bone_name:
						target_bone = target_arm.pose.bones.get(target_bone_name)
					if source_bone_name:
						source_bone = source_arm.pose.bones.get(source_bone_name)
			
					if source_bone and target_bone:
						bone_tools.rotate_target_pose_bone_to_source_bone(source_arm,target_arm,target_bone)
			
					elif target_bone and source_bone == None:

						if context.scene.art_reset_rot_if_no_match == True:
							bone_tools.clear_rotation(target_bone)

						#special coding for knee_2_L and knee_2_R, if it's not found, then reset rotation
						knee_2_bones = ('knee_2_L','knee_2_R')
						for mmd_e_bone_name in knee_2_bones:
							target_bone_name_mmd_e = bone_tools.get_mmd_english_equivalent_bone_name(target_bone_name)
							if target_bone_name_mmd_e == mmd_e_bone_name:
								bone_tools.clear_rotation(target_bone)

				# Restore the stored function by appending it back
				if stored_handler:
					bpy.app.handlers.depsgraph_update_post.append(stored_handler)
			
		return {'FINISHED'}