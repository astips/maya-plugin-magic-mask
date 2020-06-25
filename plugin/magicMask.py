# -*- coding: utf-8 -*-

import sys
import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaUI as OpenMayaUI
import maya.api.OpenMayaRender as OpenMayaRender
import maya.api.OpenMayaAnim as OpenMayaAnim
import pymel.core as pm


PLUGIN_VERSION = '1.0.0'
NODE_NAME = 'magicMask'
NODE_ID = OpenMaya.MTypeId(0x87072)

CROP_MAP = {
    'format': 1.0,
    'square': 1.0,
    '4:3': 4.0/3.0,
    '16:9': 16.0/9.0,
    '14:9': 14.0/9.0,
    '1.66:1': 1.66,
    '1.85:1': 1.85,
    '2.35:1': 2.35
}

FONT_WEIGHT_MAP = {
    'Normal': 50,  # kWeightNormal = 50
    'DemiBold': 63,  # kWeightDemiBold = 63
    'Bold': 75,  # kWeightBold = 75
}


def maya_useNewAPI():
    pass


class MagicMaskData(OpenMaya.MUserData):
    def __init__(self):
        super(MagicMaskData, self).__init__(False)


class MagicMaskNode(OpenMayaUI.MPxLocatorNode):

    DRAW_DB_CLASSIFICATION = 'drawdb/geometry/magicmask'
    DRAW_REGISTRANT_ID = 'MagicMaskNode'

    TEXT_ATTRIBUTES = [
        'top_left_text', 'top_center_text', 'top_right_text',
        'bottom_left_text', 'bottom_center_text', 'bottom_right_text'
    ]
    TEXT_POSITION_NUMBER = 6

    def __init__(self):
        OpenMayaUI.MPxLocatorNode.__init__(self)

    def excludeAsLocator(self):
        return False

    def postConstructor(self):
        this_object = self.thisMObject()
        node = OpenMaya.MFnDagNode(this_object)

        hidden_attributes = [
            u'localPosition', u'localPositionX', u'localPositionY', u'localPositionZ',
            u'localScale', u'localScaleX', u'localScaleY', u'localScaleZ'
        ]
        for attribute in hidden_attributes:
            attr_object = node.attribute(attribute)
            plug = OpenMaya.MPlug(this_object, attr_object)
            plug.isLocked = True
            plug.isChannelBox = False
            plug.isKeyable = False

    @classmethod
    def initialize(cls):
        typed_attr = OpenMaya.MFnTypedAttribute()
        numeric_attr = OpenMaya.MFnNumericAttribute()
        enum_attr = OpenMaya.MFnEnumAttribute()

        for text_attribute in cls.TEXT_ATTRIBUTES:
            string_data = OpenMaya.MFnStringData().create('Placeholder')
            attr = typed_attr.create(text_attribute, text_attribute, OpenMaya.MFnData.kString, string_data)
            cls.addAttribute(attr)

        cls.top_text_padding = numeric_attr.create(
            'top_text_padding', 'top_text_padding', OpenMaya.MFnNumericData.kInt, 20
        )
        cls.addAttribute(cls.top_text_padding)

        cls.bottom_text_padding = numeric_attr.create(
            'bottom_text_padding', 'bottom_text_padding', OpenMaya.MFnNumericData.kInt, 20
        )
        cls.addAttribute(cls.bottom_text_padding)

        cls.top_text_color = numeric_attr.createColor('top_text_color', 'top_text_color')
        numeric_attr.default = (1.0, 1.0, 1.0)
        cls.addAttribute(cls.top_text_color)

        cls.bottom_text_color = numeric_attr.createColor('bottom_text_color', 'bottom_text_color')
        numeric_attr.default = (1.0, 1.0, 1.0)
        cls.addAttribute(cls.bottom_text_color)

        cls.top_text_alpha = numeric_attr.create(
            'top_text_alpha', 'top_text_alpha', OpenMaya.MFnNumericData.kFloat, 1.0
        )
        numeric_attr.setMin(0.0)
        numeric_attr.setMax(1.0)
        cls.addAttribute(cls.top_text_alpha)

        cls.bottom_text_alpha = numeric_attr.create(
            'bottom_text_alpha', 'bottom_text_alpha', OpenMaya.MFnNumericData.kFloat, 1.0
        )
        numeric_attr.setMin(0.0)
        numeric_attr.setMax(1.0)
        cls.addAttribute(cls.bottom_text_alpha)

        cls.top_text_font_weight = enum_attr.create('top_text_font_weight', 'top_text_font_weight', 2)
        enum_attr.addField('Normal', 0)
        enum_attr.addField('DemiBold', 1)
        enum_attr.addField('Bold', 2)
        cls.addAttribute(cls.top_text_font_weight)

        cls.bottom_text_font_weight = enum_attr.create('bottom_text_font_weight', 'bottom_text_font_weight', 2)
        enum_attr.addField('Normal', 0)
        enum_attr.addField('DemiBold', 1)
        enum_attr.addField('Bold', 2)
        cls.addAttribute(cls.bottom_text_font_weight)

        cls.top_text_scale = numeric_attr.create(
            'top_text_scale', 'top_text_scale', OpenMaya.MFnNumericData.kFloat, 1.0
        )
        numeric_attr.setMin(0.2)
        numeric_attr.setMax(5.0)
        cls.addAttribute(cls.top_text_scale)

        cls.bottom_text_scale = numeric_attr.create(
            'bottom_text_scale', 'bottom_text_scale', OpenMaya.MFnNumericData.kFloat, 1.0
        )
        numeric_attr.setMin(0.2)
        numeric_attr.setMax(5.0)
        cls.addAttribute(cls.bottom_text_scale)

        cls.top_border_enabled = numeric_attr.create(
            'top_border_enabled', 'top_border_enabled', OpenMaya.MFnNumericData.kBoolean, True
        )
        cls.addAttribute(cls.top_border_enabled)

        cls.bottom_border_enabled = numeric_attr.create(
            'bottom_border_enabled', 'bottom_border_enabled', OpenMaya.MFnNumericData.kBoolean, True
        )
        cls.addAttribute(cls.bottom_border_enabled)

        cls.border_color = numeric_attr.createColor('border_color', 'border_color')
        numeric_attr.default = (0.0, 0.0, 0.0)
        cls.addAttribute(cls.border_color)

        cls.border_alpha = numeric_attr.create(
            'border_alpha', 'border_alpha', OpenMaya.MFnNumericData.kFloat, 1.0
        )
        numeric_attr.setMin(0.0)
        numeric_attr.setMax(1.0)
        cls.addAttribute(cls.border_alpha)

        cls.border_scale = numeric_attr.create('border_scale', 'border_scale', OpenMaya.MFnNumericData.kFloat, 1.0)
        numeric_attr.setMin(0.5)
        numeric_attr.setMax(2.0)
        cls.addAttribute(cls.border_scale)

        cls.crop_enabled = numeric_attr.create(
            'crop_enabled', 'crop_enabled', OpenMaya.MFnNumericData.kBoolean, False
        )
        cls.addAttribute(cls.crop_enabled)

        cls.crop_preset = enum_attr.create('crop_preset', 'crop_preset', 0)
        enum_attr.addField('format', 0)
        enum_attr.addField('square', 1)
        enum_attr.addField('4:3', 2)
        enum_attr.addField('16:9', 3)
        enum_attr.addField('14:9', 4)
        enum_attr.addField('1.66:1', 5)
        enum_attr.addField('1.85:1', 6)
        enum_attr.addField('2.35:1', 7)
        cls.addAttribute(cls.crop_preset)

        cls.crop_use_custom = numeric_attr.create(
            'crop_use_custom', 'crop_use_custom', OpenMaya.MFnNumericData.kBoolean, False
        )
        cls.addAttribute(cls.crop_use_custom)

        cls.crop_custom_width = numeric_attr.create(
            'crop_custom_width', 'crop_custom_width', OpenMaya.MFnNumericData.kInt, 1920
        )
        cls.addAttribute(cls.crop_custom_width)

        cls.crop_custom_height = numeric_attr.create(
            'crop_custom_height', 'crop_custom_height', OpenMaya.MFnNumericData.kInt, 1080
        )
        cls.addAttribute(cls.crop_custom_height)

        cls.counter_position = numeric_attr.create(
            'counter_position', 'counter_position', OpenMaya.MFnNumericData.kInt, 6
        )
        numeric_attr.setMin(0)
        numeric_attr.setMax(6)
        cls.addAttribute(cls.counter_position)

        cls.counter_padding = numeric_attr.create(
            'counter_padding', 'counter_padding', OpenMaya.MFnNumericData.kInt, 4
        )
        numeric_attr.setMin(2)
        numeric_attr.setMax(6)
        cls.addAttribute(cls.counter_padding)

        cls.frame_offset = numeric_attr.create(
            'frame_offset', 'frame_offset', OpenMaya.MFnNumericData.kInt, 0
        )
        cls.addAttribute(cls.frame_offset)

        cls.cut_frame_enabled = numeric_attr.create(
            'cut_frame_enabled', 'cut_frame_enabled', OpenMaya.MFnNumericData.kBoolean, False
        )
        cls.addAttribute(cls.cut_frame_enabled)

        cls.cut_in = numeric_attr.create(
            'cut_in', 'cut_in', OpenMaya.MFnNumericData.kInt, 1001
        )
        cls.addAttribute(cls.cut_in)

        cls.cut_out = numeric_attr.create(
            'cut_out', 'cut_out', OpenMaya.MFnNumericData.kInt, 1001
        )
        cls.addAttribute(cls.cut_out)

        cls.focal_length_position = numeric_attr.create(
            'focal_length_position', 'focal_length_position', OpenMaya.MFnNumericData.kInt, 6
        )
        numeric_attr.setMin(0)
        numeric_attr.setMax(6)
        cls.addAttribute(cls.focal_length_position)

    @classmethod
    def creator(cls):
        return cls()

    def draw(self, view, obj_path, style, status):
        # mask_obj = self.thisMObject()
        # mask_node = OpenMaya.MFnDagNode(mask_obj)
        #
        # camera_path = view.getCamera()
        # camera = OpenMaya.MFnCamera(camera_path)
        # ncp = camera.nearClippingPlane + 0.001
        # camera_aspect_ratio = camera.aspectRatio()
        # device_aspect_ratio = pm.general.getAttr('defaultResolution.deviceAspectRatio')
        #
        # viewport_width = view.portWidth()
        # viewport_height = view.portHeight()
        # viewport_aspect_ratio = viewport_width / float(viewport_height)
        #
        # view.beginGL()
        #
        # import maya.OpenMayaRender as OpenMayaRender_VP1  # drawing in VP1 views will be done using V1 Python APIs:
        # gl_renderer = OpenMayaRender_VP1.MHardwareRenderer.theRenderer()
        # gl_ft = gl_renderer.glFunctionTable()
        #
        # gl_ft.glPushAttrib(OpenMayaRender_VP1.MGL_CURRENT_BIT)
        # gl_ft.glDisable(OpenMayaRender_VP1.MGL_CULL_FACE)
        #
        # gl_ft.glBegin(OpenMayaRender_VP1.MGL_QUADS)
        #
        # gl_ft.glVertex3d(-10, -10, -1*ncp)
        # gl_ft.glVertex3d(10, -10, -1*ncp)
        # gl_ft.glVertex3d(10, 10, -1*ncp)
        # gl_ft.glVertex3d(-10, 10, -1*ncp)
        #
        # gl_ft.glEnd()
        #
        # view.endGL()
        # view.drawText(
        #     'AAAA', OpenMaya.MPoint(top_text_padding, mask_y_top-border_height), OpenMayaUI.M3dView.kLeft
        # )
        pass


# Viewport 2.0 override implementation
class MagicMaskDrawOverride(OpenMayaRender.MPxDrawOverride):

    def __init__(self, obj):
        super(MagicMaskDrawOverride, self).__init__(obj, MagicMaskDrawOverride.draw)

    def supportedDrawAPIs(self):
        return (
            OpenMayaRender.MRenderer.kAllDevices
        )

    def isBounded(self, obj_path, camera_path):
        return False

    def boundingBox(self, obj_path, camera_path):
        return OpenMaya.MBoundingBox()

    def prepareForDraw(self, obj_path, camera_path, frame_context, old_data):
        data = old_data
        if not isinstance(data, MagicMaskData):
            data = MagicMaskData()

        mask_node = OpenMaya.MFnDagNode(obj_path)

        data.text_fields = []
        for attribute in MagicMaskNode.TEXT_ATTRIBUTES:
            data.text_fields.append(mask_node.findPlug(attribute, False).asString())

        data.top_text_padding = mask_node.findPlug('top_text_padding', False).asInt()
        data.bottom_text_padding = mask_node.findPlug('bottom_text_padding', False).asInt()
        data.top_text_scale = mask_node.findPlug('top_text_scale', False).asFloat()
        data.bottom_text_scale = mask_node.findPlug('bottom_text_scale', False).asFloat()

        top_text_color_r = mask_node.findPlug('top_text_colorR', False).asFloat()
        top_text_color_g = mask_node.findPlug('top_text_colorG', False).asFloat()
        top_text_color_b = mask_node.findPlug('top_text_colorB', False).asFloat()
        top_text_color_a = mask_node.findPlug('top_text_alpha', False).asFloat()
        data.top_text_color = OpenMaya.MColor(
            (top_text_color_r, top_text_color_g, top_text_color_b, top_text_color_a)
        )
        top_text_font_weight_plug = mask_node.findPlug('top_text_font_weight', False)
        top_text_font_weight_attr = OpenMaya.MFnEnumAttribute(top_text_font_weight_plug.attribute())
        data.top_text_font_weight = FONT_WEIGHT_MAP.get(
            top_text_font_weight_attr.fieldName(top_text_font_weight_plug.asShort())
        )

        bottom_text_color_r = mask_node.findPlug('bottom_text_colorR', False).asFloat()
        bottom_text_color_g = mask_node.findPlug('bottom_text_colorG', False).asFloat()
        bottom_text_color_b = mask_node.findPlug('bottom_text_colorB', False).asFloat()
        bottom_text_color_a = mask_node.findPlug('bottom_text_alpha', False).asFloat()
        data.bottom_text_color = OpenMaya.MColor(
            (bottom_text_color_r, bottom_text_color_g, bottom_text_color_b, bottom_text_color_a)
        )
        bottom_text_font_weight_plug = mask_node.findPlug('bottom_text_font_weight', False)
        bottom_text_font_weight_attr = OpenMaya.MFnEnumAttribute(bottom_text_font_weight_plug.attribute())
        data.bottom_text_font_weight = FONT_WEIGHT_MAP.get(
            bottom_text_font_weight_attr.fieldName(bottom_text_font_weight_plug.asShort())
        )

        border_color_r = mask_node.findPlug('border_colorR', False).asFloat()
        border_color_g = mask_node.findPlug('border_colorG', False).asFloat()
        border_color_b = mask_node.findPlug('border_colorB', False).asFloat()
        border_color_a = mask_node.findPlug('border_alpha', False).asFloat()
        data.border_color = OpenMaya.MColor((border_color_r, border_color_g, border_color_b, border_color_a))

        counter_position = mask_node.findPlug('counter_position', False).asInt()
        if 0 <= counter_position < MagicMaskNode.TEXT_POSITION_NUMBER:
            offset_frame = mask_node.findPlug('frame_offset', False).asInt()
            counter_padding = mask_node.findPlug('counter_padding', False).asInt()
            current_frame = int(OpenMayaAnim.MAnimControl.currentTime().value)
            end_frame = int(OpenMayaAnim.MAnimControl.maxTime().value)

            frame_string = '{0} / {1}'.format(
                str(current_frame+offset_frame).zfill(counter_padding),
                str(end_frame+offset_frame).zfill(counter_padding)
            )
            cut_frame_enabled = mask_node.findPlug('cut_frame_enabled', False).asBool()
            if cut_frame_enabled:
                cut_in = mask_node.findPlug('cut_in', False).asInt()
                cut_out = mask_node.findPlug('cut_out', False).asInt()
                cut_string = '{0}-{1}'.format(cut_in, cut_out)
                data.text_fields[counter_position] = '{0} | {1}'.format(cut_string, frame_string)
            else:
                data.text_fields[counter_position] = frame_string

        data.top_border_enabled = mask_node.findPlug('top_border_enabled', False).asBool()
        data.bottom_border_enabled = mask_node.findPlug('bottom_border_enabled', False).asBool()
        data.border_scale = mask_node.findPlug('border_scale', False).asFloat()

        data.crop_enabled = mask_node.findPlug('crop_enabled', False).asBool()
        crop_preset_plug = mask_node.findPlug('crop_preset', False)
        crop_preset_attr = OpenMaya.MFnEnumAttribute(crop_preset_plug.attribute())
        data.crop_preset = CROP_MAP.get(crop_preset_attr.fieldName(crop_preset_plug.asShort()))
        data.crop_use_custom = mask_node.findPlug('crop_use_custom', False).asBool()
        data.crop_custom_width = mask_node.findPlug('crop_custom_width', False).asFloat()
        data.crop_custom_height = mask_node.findPlug('crop_custom_height', False).asFloat()

        focal_length_position = mask_node.findPlug('focal_length_position', False).asInt()
        if 0 <= focal_length_position < MagicMaskNode.TEXT_POSITION_NUMBER:
            camera_path = frame_context.getCurrentCameraPath()
            camera = OpenMaya.MFnCamera(camera_path)
            focal_length_string = 'Focal Length: %.2f' % camera.focalLength
            data.text_fields[focal_length_position] = focal_length_string

        return data

    def hasUIDrawables(self):
        return True

    def addUIDrawables(self, obj_path, draw_manager, frame_context, data):
        if not isinstance(data, MagicMaskData):
            return
        camera_path = frame_context.getCurrentCameraPath()
        camera = OpenMaya.MFnCamera(camera_path)
        camera_aspect_ratio = camera.aspectRatio()
        device_aspect_ratio = pm.general.getAttr('defaultResolution.deviceAspectRatio')

        viewport_x, viewport_y, viewport_width, viewport_height = frame_context.getViewportDimensions()
        viewport_aspect_ratio = viewport_width / float(viewport_height)

        scale = 1.0
        if camera.filmFit == OpenMaya.MFnCamera.kHorizontalFilmFit:
            mask_width = viewport_width / camera.overscan
            mask_height = mask_width / device_aspect_ratio
        elif camera.filmFit == OpenMaya.MFnCamera.kVerticalFilmFit:
            mask_height = viewport_height / camera.overscan
            mask_width = mask_height * device_aspect_ratio
        elif camera.filmFit in (OpenMaya.MFnCamera.kFillFilmFit, OpenMaya.MFnCamera.kOverscanFilmFit):
            if camera_aspect_ratio > device_aspect_ratio:
                scale = device_aspect_ratio / camera_aspect_ratio
            elif viewport_aspect_ratio < camera_aspect_ratio:
                scale = min(camera_aspect_ratio, device_aspect_ratio) / viewport_aspect_ratio
            else:
                pass
            if camera.filmFit == OpenMaya.MFnCamera.kFillFilmFit:
                mask_width = viewport_width / camera.overscan * scale
                mask_height = mask_width / device_aspect_ratio
            else:
                mask_height = viewport_height / camera.overscan / scale
                mask_width = mask_height * device_aspect_ratio
        else:
            OpenMaya.MGlobal.displayError('[MagicMask] Unknown Film Fit Value')
            return

        mask_x = 0.5 * (viewport_width - mask_width)
        mask_y_top = 0.5 * (viewport_height + mask_height)
        mask_y_bottom = 0.5 * (viewport_height - mask_height)

        if not data.crop_enabled:
            border_height = int(0.1 * mask_height * data.border_scale)
        else:
            if not data.crop_use_custom:
                border_height = int((mask_height - mask_width / data.crop_preset) / 2.0)
            else:
                border_height = int(
                    (mask_height - mask_width / (data.crop_custom_width / data.crop_custom_height)) / 2.0
                )

        if border_height <= 0:
            OpenMaya.MGlobal.displayWarning(
                "MagicMask's height pixel <= 0 ({0}), current crop preset not "
                "suit for current scene render size.".format(border_height)
            )
            return
        background_size = (int(mask_width), border_height)

        # draw mask
        draw_manager.beginDrawable()

        if data.top_border_enabled:
            draw_manager.text2d(
                OpenMaya.MPoint(mask_x, mask_y_top-border_height), ' ',
                alignment=OpenMayaRender.MUIDrawManager.kLeft,
                backgroundSize=background_size,
                backgroundColor=data.border_color,
                dynamic=False
            )
        if data.bottom_border_enabled:
            draw_manager.text2d(
                OpenMaya.MPoint(mask_x, mask_y_bottom), ' ',
                alignment=OpenMayaRender.MUIDrawManager.kLeft,
                backgroundSize=background_size,
                backgroundColor=data.border_color,
                dynamic=False
            )

        draw_manager.setColor(data.top_text_color)
        draw_manager.setFontSize(int(border_height * 0.25 * data.top_text_scale))
        draw_manager.setFontWeight(data.top_text_font_weight)
        self.draw_text(
            draw_manager, OpenMaya.MPoint(mask_x+data.top_text_padding, mask_y_top-border_height),
            data.text_fields[0], OpenMayaRender.MUIDrawManager.kLeft, background_size
        )
        self.draw_text(
            draw_manager, OpenMaya.MPoint(viewport_width*0.5, mask_y_top-border_height),
            data.text_fields[1], OpenMayaRender.MUIDrawManager.kCenter, background_size
        )
        self.draw_text(
            draw_manager, OpenMaya.MPoint(mask_x+mask_width-data.top_text_padding, mask_y_top-border_height),
            data.text_fields[2], OpenMayaRender.MUIDrawManager.kRight, background_size
        )

        draw_manager.setColor(data.bottom_text_color)
        draw_manager.setFontSize(int(border_height * 0.25 * data.bottom_text_scale))
        draw_manager.setFontWeight(data.bottom_text_font_weight)
        self.draw_text(
            draw_manager, OpenMaya.MPoint(mask_x+data.bottom_text_padding, mask_y_bottom),
            data.text_fields[3], OpenMayaRender.MUIDrawManager.kLeft, background_size
        )
        self.draw_text(
            draw_manager, OpenMaya.MPoint(viewport_width*0.5, mask_y_bottom),
            data.text_fields[4], OpenMayaRender.MUIDrawManager.kCenter, background_size
        )
        self.draw_text(
            draw_manager, OpenMaya.MPoint(mask_x+mask_width-data.bottom_text_padding, mask_y_bottom),
            data.text_fields[5], OpenMayaRender.MUIDrawManager.kRight, background_size
        )

        draw_manager.endDrawable()

    @staticmethod
    def draw_text(draw_manager, position, text, alignment, background_size):
        if not len(text):
            return
        draw_manager.text2d(
            position, text, alignment=alignment,
            backgroundSize=background_size,
            backgroundColor=OpenMaya.MColor((0.0, 0.0, 0.0, 0.0)),
            dynamic=False
        )

    @staticmethod
    def creator(obj):
        return MagicMaskDrawOverride(obj)

    @staticmethod
    def draw(context, data):
        return


def initializePlugin(obj):
    plugin = OpenMaya.MFnPlugin(obj, 'astips', PLUGIN_VERSION, 'Any')
    try:
        plugin.registerNode(
            NODE_NAME, NODE_ID, MagicMaskNode.creator, MagicMaskNode.initialize,
            OpenMaya.MPxNode.kLocatorNode, MagicMaskNode.DRAW_DB_CLASSIFICATION
        )
    except SyntaxError:
        sys.stderr.write('Loading Error')
        raise Exception('Failed to register magicMask Node.')

    try:
        OpenMayaRender.MDrawRegistry.registerDrawOverrideCreator(
            MagicMaskNode.DRAW_DB_CLASSIFICATION,
            MagicMaskNode.DRAW_REGISTRANT_ID,
            MagicMaskDrawOverride.creator
        )
    except SyntaxError:
        sys.stderr.write('Loading Error')
        raise Exception('Failed to register magicMaskDrawOverride.')


def uninitializePlugin(obj):
    plugin = OpenMaya.MFnPlugin(obj)
    try:
        OpenMayaRender.MDrawRegistry.deregisterDrawOverrideCreator(
            MagicMaskNode.DRAW_DB_CLASSIFICATION,
            MagicMaskNode.DRAW_REGISTRANT_ID
        )
    except SyntaxError:
        sys.stderr.write('Removing Error')
        raise Exception('Failed to de-register magicMaskDrawOverride.')

    try:
        plugin.deregisterNode(NODE_ID)
    except SyntaxError:
        sys.stderr.write('Removing Error')
        raise Exception('Failed to de-register magicMask Node.')


PRESS_PROPERTIES = [
    u'visibility',
    u'message', u'caching', u'isHistoricallyInteresting', u'nodeState', u'binMembership',
    u'frozen', u'hyperLayout', u'isCollapsed', u'blackBox', u'borderConnections',
    u'isHierarchicalConnection', u'publishedNodeInfo',
    u'rmbCommand', u'templateName', u'templatePath', u'viewName', u'iconName',
    u'viewMode', u'templateVersion', u'uiTreatment', u'customTreatment',
    u'creator', u'creationDate',
    u'containerType', u'boundingBox', u'boundingBoxSize', u'center',
    u'parentMatrix', u'parentInverseMatrix',
    u'intermediateObject', u'template', u'ghosting',
    u'instObjGroups', u'objectColorRGB', u'wireColorRGB',
    u'useObjectColor', u'objectColor', u'drawOverride', u'overrideDisplayType',
    u'overrideLevelOfDetail', u'overrideShading', u'overrideTexturing', u'overridePlayback',
    u'overrideEnabled', u'overrideVisibility', u'hideOnPlayback', u'overrideRGBColors',
    u'overrideColor', u'overrideColorRGB',
    u'lodVisibility', u'selectionChildHighlighting', u'renderInfo', u'identification', u'layerRenderable',
    u'layerOverrideColor', u'renderLayerInfo',
    u'ghostingControl', u'ghostCustomSteps', u'ghostPreSteps', u'ghostPostSteps', u'ghostStepSize', u'ghostFrames',
    u'ghostColorPre', u'ghostColorPreA', u'ghostColorPostA', u'ghostColorPost',
    u'ghostRangeStart', u'ghostRangeEnd', u'ghostDriver',
    u'hiddenInOutliner', u'useOutlinerColor', u'outlinerColor',
    u'renderType', u'renderVolume', u'visibleFraction', u'hardwareFogMultiplier', u'motionBlur',
    u'visibleInReflections', u'visibleInRefractions', u'castsShadows', u'receiveShadows', u'asBackground',
    u'maxVisibilitySamplesOverride', u'maxVisibilitySamples', u'geometryAntialiasingOverride',
    u'antialiasingLevel', u'shadingSamplesOverride', u'shadingSamples', u'maxShadingSamples',
    u'volumeSamplesOverride', u'volumeSamples', u'depthJitter', u'ignoreSelfShadowing', u'primaryVisibility',
    u'localPosition', u'localPositionX', u'localPositionY', u'localPositionZ',
    u'localScale', u'localScaleX', u'localScaleY', u'localScaleZ',
    u'referenceObject', u'compInstObjGroups', u'underWorldObject',  u'worldPosition'
]


class NodeTemplate(pm.ui.AETemplate):
    def __init__(self, node_name):
        pm.ui.AETemplate.__init__(self, node_name)

    def suppress_attributes(self):
        self.beginNoOptimize()
        for attr in PRESS_PROPERTIES:
            self.suppress(attr)
        self.endNoOptimize()


class AEmagicMaskTemplate(NodeTemplate):
    def __init__(self, node_name):
        NodeTemplate.__init__(self, node_name)
        self.current_node = None
        self.setup_layout()

    def setup_layout(self):
        self.beginScrollLayout()

        self.beginLayout('Top Text', collapse=False)
        self.addControl('top_left_text', label='Left', preventOverride=True)
        self.addControl('top_center_text', label='Center', preventOverride=False)
        self.addControl('top_right_text', label='Right', preventOverride=False)
        self.addSeparator()
        self.addControl('top_text_padding', label='Padding', preventOverride=False)
        self.addControl('top_text_font_weight', label='Font', preventOverride=False)
        self.addControl('top_text_scale', label='Scale', preventOverride=False)
        self.addControl('top_text_color', label='Color', preventOverride=False)
        self.addControl('top_text_alpha', label='Alpha', preventOverride=False)
        self.endLayout()

        self.beginLayout('Bottom Text', collapse=False)
        self.addControl('bottom_left_text', label='Left', preventOverride=True)
        self.addControl('bottom_center_text', label='Center', preventOverride=False)
        self.addControl('bottom_right_text', label='Right', preventOverride=False)
        self.addSeparator()
        self.addControl('bottom_text_padding', label='Padding', preventOverride=False)
        self.addControl('bottom_text_font_weight', label='Font', preventOverride=False)
        self.addControl('bottom_text_scale', label='Scale', preventOverride=False)
        self.addControl('bottom_text_color', label='Color', preventOverride=False)
        self.addControl('bottom_text_alpha', label='Alpha', preventOverride=False)
        self.endLayout()

        self.beginLayout('Border', collapse=False)
        self.addControl('top_border_enabled', label='Top Enabled', preventOverride=True)
        self.addControl('bottom_border_enabled', label='Bottom Enabled', preventOverride=True)
        self.addControl('border_color', label='Color', preventOverride=True)
        self.addControl('border_alpha', label='Alpha', preventOverride=True)
        self.addControl('border_scale', label='Scale', preventOverride=True)
        self.beginLayout('Crop', collapse=False)
        self.addControl(
            'crop_enabled',
            label='Enabled',
            preventOverride=True,
            changeCommand=self.dim_crop_use_custom
        )
        self.addControl('crop_preset', label='Preset', preventOverride=True)
        self.addSeparator()
        self.addControl(
            'crop_use_custom',
            label='Custom Resolution',
            preventOverride=True,
            changeCommand=self.dim_crop_resolution
        )
        self.addControl('crop_custom_width', label='Width', preventOverride=True)
        self.addControl('crop_custom_height', label='Height', preventOverride=True)
        self.endLayout()
        self.endLayout()

        self.beginLayout('Frame', collapse=False)
        self.addControl('counter_position', label='Position', preventOverride=True)
        self.addControl('counter_padding', label='Padding', preventOverride=True)
        self.addSeparator()
        self.addControl('frame_offset', label='Offset', preventOverride=True)
        self.addSeparator()
        self.addControl(
            'cut_frame_enabled', label='Cut Enabled', preventOverride=True, changeCommand=self.dim_cut
        )
        self.addControl('cut_in', label='In', preventOverride=True)
        self.addControl('cut_out', label='Out', preventOverride=True)
        self.endLayout()

        self.beginLayout('Camera Focal Length', collapse=False)
        self.addControl('focal_length_position', label='Position', preventOverride=True)
        self.endLayout()

        # self.addExtraControls()
        self.suppress_attributes()
        self.endScrollLayout()

    def dim_crop_use_custom(self, plug):
        if self.current_node is None:
            self.current_node = pm.general.PyNode(plug.split('.')[0])
        value = 1 - self.current_node.crop_enabled.get()
        self.dimControl(self.current_node, 'crop_preset', value)
        self.dimControl(self.current_node, 'crop_use_custom', value)
        self.dimControl(self.current_node, 'crop_custom_width', value)
        self.dimControl(self.current_node, 'crop_custom_height', value)
        if not value:
            self.dim_crop_resolution(plug)

    def dim_crop_resolution(self, plug):
        if self.current_node is None:
            self.current_node = pm.general.PyNode(plug.split('.')[0])
        value = 1 - self.current_node.crop_use_custom.get()
        self.dimControl(self.current_node, 'crop_custom_width', value)
        self.dimControl(self.current_node, 'crop_custom_height', value)

    def dim_cut(self, plug):
        if self.current_node is None:
            self.current_node = pm.general.PyNode(plug.split('.')[0])
        value = 1 - self.current_node.cut_frame_enabled.get()
        self.dimControl(self.current_node, 'cut_in', value)
        self.dimControl(self.current_node, 'cut_out', value)
