import inviwopy
# import inviwopy.glm as glm
import numpy as np
import h5py
from envisionpy.utils.exceptions import *
from .Subnetwork import Subnetwork

class VolumeSubnetwork(Subnetwork):
    '''
    Manages a subnetwork for generic volume rendering.
    Not used directly in any visualisation but inherited by others.
    Used for charge density, ELF, fermi surface, partial charge, visualisations.
    '''
    def __init__(self, inviwoApp, hdf5_path, hdf5_outport, xpos=0, ypos=0, multichannel=False):
        Subnetwork.__init__(self, inviwoApp)
        self.is_multichannel = multichannel
        self.transperancy_before = True
        self.tf_enabled = True
        self.iso_enabled = False
        self.iso_color = [1, 1, 1, 1]
        self.iso_value = 0.5

        self.setup_network(hdf5_path, hdf5_outport, xpos, ypos)

        self.set_texture_wrap_mode(2)
        self.set_slice_background(
            inviwopy.glm.vec4(0,0,0,1),
            inviwopy.glm.vec4(1,1,1,1),3,0)
        self.clear_tf()
        self.set_plane_normal()
        self.set_iso_surface(0.5, [1, 1, 1, 1])
        self.toggle_iso(False)

    def show(self, show_volume=True, show_slice=False):
        if show_volume:
            self.get_processor('VolumeCanvas').widget.show()
        if show_slice:
            self.get_processor('SliceCanvas').widget.show()

    def hide(self, hide_volume=True, hide_slice=True):
        if hide_volume:
            self.get_processor('VolumeCanvas').widget.hide()
        if hide_slice:
            self.get_processor('SliceCanvas').widget.hide()

    def get_ui_data(self):
        rc = self.get_processor('Raycaster')
        vCanvas = self.get_processor('VolumeCanvas')
        sCanvas = self.get_processor('SliceCanvas')
        selection = self.get_processor('Hdf5Selection')
        volumeSlice = self.get_processor('VolumeSlice')

        return [
            not vCanvas.widget.visibility,
            [selection.volumeSelection.selectedValue, selection.volumeSelection.values],
            rc.lighting.shadingMode.selectedDisplayName,
            self.get_background_info(),
            self.transperancy_before,
            self.get_tf_points(),
            [self.iso_enabled, self.iso_value, self.iso_color],
            [
                sCanvas.widget.visibility,
                rc.positionindicator.enable.value,
                volumeSlice.planePosition.value.x,
                volumeSlice.trafoGroup.imageScale.value,
                volumeSlice.trafoGroup.volumeWrapping.selectedDisplayName,
                [volumeSlice.planeNormal.value.x, volumeSlice.planeNormal.value.y, volumeSlice.planeNormal.value.z]
            ]
        ]

# ------------------------------------------
# ------- Property control functions -------

    def set_mask(self, maskMin, maskMax, idx=None):
    # Set the mask of the transfer function
    # Only volume densities between maskMin and maskMax are visible after this
        raycaster = self.get_processor('Raycaster')
        if not self.is_multichannel:
            raycaster.isotfComposite.tf.setMask(maskMin, maskMax)
        else:
            getattr(raycaster, 'transfer-functions').transferFunction1.setMask(maskMin, maskMax)
            getattr(raycaster, 'transfer-functions').transferFunction2.setMask(maskMin, maskMax)
            getattr(raycaster, 'transfer-functions').transferFunction3.setMask(maskMin, maskMax)
            getattr(raycaster, 'transfer-functions').transferFunction4.setMask(maskMin, maskMax)

    def toggle_transperancy_before(self, enable):
    # Toggle full transperancy before first tf point.
        self.transperancy_before = enable
        self.tf_changed()

    def tf_changed(self):
        if self.transperancy_before and len(self.get_tf_points()) > 0:
            lowestVal = self.get_tf_points()[0][0]
        else:
            lowestVal = 0
        self.set_mask(lowestVal, 1)

        # Copy the volume transferfunction to the slice transferfunction
        # Adds a white point just before the first one aswell
        volumeSlice = self.get_processor('VolumeSlice')
        volumeSlice.tfGroup.transferFunction.clear()
        tf_points = self.get_tf_points()
        for point in tf_points:
            volumeSlice.tfGroup.transferFunction.add(point[0], inviwopy.glm.vec4(point[1][0], point[1][1], point[1][2], 1))
        if self.transperancy_before and len(tf_points) > 0 and tf_points[0][0] != 0:
            volumeSlice.tfGroup.transferFunction.add(0.99*tf_points[0][0], inviwopy.glm.vec4(1.0, 1.0, 1.0, 1.0))

    def clear_tf(self):
    # Clears the transfer function of all points
        Raycaster = self.get_processor('Raycaster')
        if not self.is_multichannel:
            Raycaster.isotfComposite.tf.clear()
        else:
            getattr(Raycaster, 'transfer-functions').transferFunction1.clear()
            getattr(Raycaster, 'transfer-functions').transferFunction2.clear()
            getattr(Raycaster, 'transfer-functions').transferFunction3.clear()
            getattr(Raycaster, 'transfer-functions').transferFunction4.clear()
        self.tf_changed()

    def set_tf_points(self, points):
    # Sets all transfer function points from an array of tf poitns.
        raycaster = self.get_processor('Raycaster')
        if not self.is_multichannel:
            tfProperty = raycaster.isotfComposite.tf
        else:
            tfProperty = getattr(raycaster, 'transfer-functions').transferFunction1
        tfProperty.clear()

        for point in points:
            glm_col = inviwopy.glm.vec4(point[1][0], point[1][1], point[1][2], point[1][3])
            tfProperty.add(point[0], glm_col)

        if self.is_multichannel:
            getattr(raycaster, 'transfer-functions').transferFunction2.value = tfProperty.value
            getattr(raycaster, 'transfer-functions').transferFunction3.value = tfProperty.value
            getattr(raycaster, 'transfer-functions').transferFunction4.value = tfProperty.value
        self.tf_changed()

    def get_tf_points(self):
    # Return a list of all the transferfunction points. list element: [value, [color]]
        Raycaster = self.get_processor('Raycaster')
        if not self.is_multichannel:
            tf_property = Raycaster.isotfComposite.tf
        else:
            tf_property = getattr(Raycaster, 'transfer-functions').transferFunction1
        point_list = [[x.pos, [x.color[0], x.color[1], x.color[2], x.color[3]]] for x in tf_property.getValues()]
        return point_list

    def add_tf_point(self, value, color):
    # Add point to the raycaster transferfunction
    # Color should be an 4-element-array containing RGBA with values in 0-1 interval.
        raycaster = self.get_processor('Raycaster')
        glm_col = inviwopy.glm.vec4(color[0], color[1], color[2], color[3])
        if not self.is_multichannel:
            raycaster.isotfComposite.tf.add(value, glm_col)
        else:
            getattr(raycaster, 'transfer-functions').transferFunction1.add(value, glm_col)
            getattr(raycaster, 'transfer-functions').transferFunction2.add(value, glm_col)
            getattr(raycaster, 'transfer-functions').transferFunction3.add(value, glm_col)
            getattr(raycaster, 'transfer-functions').transferFunction4.add(value, glm_col)
        self.tf_changed()
        return [self.get_tf_points()]

    def toggle_iso(self, enable):
        self.iso_enabled = enable
        if self.is_multichannel:
            if enable:
                self.set_iso_surface(self.iso_value, self.iso_color)
            else:
                tmp = self.iso_color[3]
                self.set_iso_surface(self.iso_value, [self.iso_color[0], self.iso_color[1], self.iso_color[2], 0])
                self.iso_color[3] = tmp
        else:
            if enable:
                self.get_processor('Raycaster').raycaster.renderingType.selectedIndex = 1
            else:
                self.get_processor('Raycaster').raycaster.renderingType.selectedIndex = 0


    def set_iso_surface(self, value, color=None):
        if color==None: color = self.iso_color
        self.iso_color = color
        self.iso_value = value
        glm_col = inviwopy.glm.vec4(color[0], color[1], color[2], color[3])
        if self.is_multichannel:
            raycaster = self.get_processor('IsoRaycaster')
            raycaster.raycaster.isoValue.value = value
            getattr(raycaster, 'transfer-functions').transferFunction1.clear()
            getattr(raycaster, 'transfer-functions').transferFunction2.clear()
            getattr(raycaster, 'transfer-functions').transferFunction3.clear()
            getattr(raycaster, 'transfer-functions').transferFunction4.clear()
            getattr(raycaster, 'transfer-functions').transferFunction1.add(value, glm_col)
            getattr(raycaster, 'transfer-functions').transferFunction2.add(value, glm_col)
            getattr(raycaster, 'transfer-functions').transferFunction3.add(value, glm_col)
            getattr(raycaster, 'transfer-functions').transferFunction4.add(value, glm_col)
        else:
            raycaster = self.get_processor('Raycaster')
            raycaster.isotfComposite.isovalues.clear()
            raycaster.isotfComposite.isovalues.add(value, glm_col)

    def set_shading_mode(self, key):
        raycaster = self.get_processor('Raycaster')
        raycaster.lighting.shadingMode.selectedDisplayName = key

    def set_volume_background(self, color_1 = None, color_2 = None, styleIndex = None, blendModeIndex = None):
    # Set the background of the volume canvas
        Background = self.get_processor("VolumeBackground")
        if styleIndex != None:
            Background.backgroundStyle.selectedIndex = styleIndex
        if color_1 != None:
            glm_col = inviwopy.glm.vec4(color_1[0], color_1[1], color_1[2], color_1[3])
            Background.bgColor1.value = glm_col
        if color_2 != None:
            glm_col = inviwopy.glm.vec4(color_2[0], color_2[1], color_2[2], color_2[3])
            Background.bgColor2.value = glm_col
        if blendModeIndex != None:
            Background.blendMode.selectedIndex = blendModeIndex

    def set_slice_background(self, color_1 = None, color_2 = None, styleIndex = None, blendModeIndex = None):
    # Set the background of the volume canvas
        Background = self.get_processor("SliceBackground")
        if styleIndex != None:
            Background.backgroundStyle.selectedIndex = styleIndex
        if color_1 != None:
            Background.bgColor1.value = color_1
        if color_2 != None:
            Background.bgColor2.value = color_2
        if blendModeIndex != None:
            Background.blendMode.selectedIndex = blendModeIndex

    def toggle_slice_plane(self, enable):
    # Set if the slice plane should be visible in the volume
        Raycaster = self.get_processor('Raycaster')
        Raycaster.positionindicator.enable.value = enable

    def set_plane_normal(self, x=0, y=1, z=0):
    # Set the normal of the slice plane
    # x, y, and z can vary between 0 and 1
        VolumeSlice = self.get_processor('VolumeSlice')
        VolumeSlice.planeNormal.value = inviwopy.glm.vec3(x, y, z)

    def set_plane_height(self, height):
    # Set the height of the slice plane
    # Height can vary between 0 and 1.
        VolumeSlice = self.get_processor('VolumeSlice')
        VolumeSlice.planePosition.value = inviwopy.glm.vec3(height, height, height)

    def set_texture_wrap_mode(self, mode):
        volumeSlice = self.get_processor('VolumeSlice')
        volumeSlice.trafoGroup.volumeWrapping.selectedIndex = mode

    def set_slice_zoom(self, zoom):
        volumeSlice = self.get_processor('VolumeSlice')
        volumeSlice.trafoGroup.imageScale.value = zoom

    def get_background_info(self):
        background = self.get_processor("VolumeBackground")
        style = background.backgroundStyle.selectedDisplayName
        col_1 = background.bgColor1.value
        col_2 = background.bgColor2.value
        return [
            [col_1.r, col_1.g, col_1.b],
            [col_2.r, col_2.g, col_2.b],
            style]

# ------------------------------------------
# ------- Network building functions -------

    def set_basis(self, basis_3x3, scale=1):
        #print(basis_3x3)
        basis_4x4 = np.identity(4)
        basis_4x4[:3,:3] = basis_3x3
        basis_4x4 = np.multiply(scale, basis_4x4)
        hdf5Volume = self.get_processor('Hdf5Selection')
        hdf5Volume.basisGroup.basis.minValue = inviwopy.glm.mat4(
            -1000,-1000,-1000,-1000,
            -1000,-1000,-1000,-1000,
            -1000,-1000,-1000,-1000,
            -1000,-1000,-1000,-1000)
        hdf5Volume.basisGroup.basis.maxValue = inviwopy.glm.mat4(
            1000,1000,1000,1000,
            1000,1000,1000,1000,
            1000,1000,1000,1000,
            1000,1000,1000,1000)
        hdf5Volume.basisGroup.basis.value = inviwopy.glm.mat4(*basis_4x4.flatten())
        meshCreator = self.get_processor('MeshCreator')
        meshCreator.scale.value = scale

    def set_hdf5_subpath(self, path):
        # Flashing canvas forces network update to refresh options.
        # Without this inviwo will not always detect and select the proper volume.
        vis = self.get_processor('VolumeCanvas').widget.visibility
        self.hide() if vis else self.show()
        self.show() if vis else self.hide()

        hdf5Path = self.get_processor('HDF5 path')
        hdf5Path.selection.selectedValue = path

    def set_volume_selection(self, key):
        # vis = self.get_processor('VolumeCanvas').widget.visibility
        # self.hide()
        # self.show()
        # self.show() if vis else self.hide() # Flashing canvas forces network update to refresh options.
        hdf5Vol = self.get_processor('Hdf5Selection')
        hdf5Vol.volumeSelection.selectedValue = key

    def setup_network(self, hdf5_path, hdf5_output, xpos, ypos):
        # Setup hdf5 to volume
        hdf5Path = self.add_processor('org.inviwo.hdf5.PathSelection', 'HDF5 path', xpos, ypos)
        hdf5Volume = self.add_processor('org.inviwo.hdf5.ToVolume', 'Hdf5Selection', xpos, ypos+3)
        self.network.addConnection(hdf5_output, hdf5Path.getInport('inport'))
        self.network.addConnection(hdf5Path.getOutport('outport'), hdf5Volume.getInport('inport'))

        # Setup volume rendering
        boundingBox = self.add_processor('org.inviwo.VolumeBoundingBox', 'Volume Bounding Box', xpos+8, ypos+6)
        meshRenderer = self.add_processor('org.inviwo.GeometryRenderGL', 'Mesh Renderer', xpos+8, ypos+9)
        cubeProxy = self.add_processor('org.inviwo.CubeProxyGeometry', 'Cube Proxy Geometry', xpos+1, ypos+6)
        entryExit = self.add_processor('org.inviwo.EntryExitPoints', 'EntryExitPoints', xpos+1, ypos+9)
        if not self.is_multichannel:
            raycaster = self.add_processor('org.inviwo.VolumeRaycaster', "Raycaster", xpos, ypos+12)
            raycaster.raycaster.renderingType.selectedIndex = 1
        else:
            raycaster = self.add_processor('org.inviwo.MultichannelRaycaster', "Raycaster", xpos, ypos+12)
            # Multichannel raycaster does not support iso+dvr mode. Two processors needed.
            isoRaycaster = self.add_processor('org.inviwo.MultichannelRaycaster', "IsoRaycaster", xpos+7, ypos+12)
            isoRaycaster.raycaster.compositingMode.selectedIndex = 6
            isoRaycaster.raycaster.samplingRate.value = 4
            isoRaycaster.raycaster.classificationMode.selectedIndex = 1
            isoRaycaster.raycaster.isoValue.value = 0
        volumeBackground = self.add_processor('org.inviwo.Background', 'VolumeBackground', xpos, ypos+15)
        volumeCanvas = self.add_processor('org.inviwo.CanvasGL', 'VolumeCanvas', xpos, ypos+18)
        self.network.addConnection(hdf5Volume.getOutport('outport'), boundingBox.getInport('volume'))
        self.network.addConnection(hdf5Volume.getOutport('outport'), cubeProxy.getInport('volume'))
        self.network.addConnection(hdf5Volume.getOutport('outport'), raycaster.getInport('volume'))
        self.network.addConnection(cubeProxy.getOutport('proxyGeometry'), entryExit.getInport('geometry'))
        self.network.addConnection(entryExit.getOutport('entry'), raycaster.getInport('entry'))
        self.network.addConnection(entryExit.getOutport('exit'), raycaster.getInport('exit'))
        self.network.addConnection(boundingBox.getOutport('mesh'), meshRenderer.getInport('geometry'))
        self.network.addConnection(meshRenderer.getOutport('image'), raycaster.getInport('bg'))
        self.network.addConnection(raycaster.getOutport('outport'), volumeBackground.getInport('inport'))
        self.network.addConnection(volumeBackground.getOutport('outport'), volumeCanvas.getInport('inport'))
        self.network.addLink(meshRenderer.camera, entryExit.camera)
        self.network.addLink(meshRenderer.camera, raycaster.camera)
        if self.is_multichannel:
            # Link up the extra iso raycaster
            self.network.addConnection(hdf5Volume.getOutport('outport'), isoRaycaster.getInport('volume'))
            self.network.addConnection(entryExit.getOutport('entry'), isoRaycaster.getInport('entry'))
            self.network.addConnection(entryExit.getOutport('exit'), isoRaycaster.getInport('exit'))
            self.network.addConnection(isoRaycaster.getOutport('outport'), meshRenderer.getInport('imageInport'))
            self.network.addLink(meshRenderer.camera, isoRaycaster.camera)

        # Setup slice rendering
        volumeSlice = self.add_processor('org.inviwo.VolumeSliceGL', 'VolumeSlice', xpos-7, ypos+12)
        sliceBackground = self.add_processor('org.inviwo.Background', 'SliceBackground', xpos-7, ypos+15)
        sliceCanvas = self.add_processor('org.inviwo.CanvasGL', 'SliceCanvas', xpos-7, ypos+18)
        self.network.addConnection(hdf5Volume.getOutport('outport'), volumeSlice.getInport('volume'))
        self.network.addConnection(volumeSlice.getOutport('outport'), sliceBackground.getInport('inport'))
        self.network.addConnection(sliceBackground.getOutport('outport'), sliceCanvas.getInport('inport'))
        self.network.addLink(volumeSlice.planePosition, raycaster.positionindicator.plane1.position)
        self.network.addLink(volumeSlice.planeNormal, raycaster.positionindicator.plane1.normal)

        # Setup slice in 3d view
        meshCreator = self.add_processor('org.inviwo.MeshCreator', 'MeshCreator', xpos-14, ypos+12)
        hfRender = self.add_processor('org.inviwo.HeightFieldRenderGL', 'HFRender', xpos-14, ypos+15)
        self.network.addConnection(meshCreator.getOutport('outport'), hfRender.getInport('geometry'))
        self.network.addConnection(sliceBackground.getOutport('outport'), hfRender.getInport('texture'))
        self.network.addLink(volumeSlice.worldPosition_, meshCreator.position1)
        self.network.addLink(meshRenderer.camera, hfRender.camera)
        self.network.addLink(volumeSlice.planeNormal, meshCreator.normal)

        raycaster.raycaster.samplingRate.value = 4
        raycaster.positionindicator.plane1.enable.value = True
        raycaster.positionindicator.plane2.enable.value = False
        raycaster.positionindicator.plane3.enable.value = False
        raycaster.positionindicator.plane1.color.value = inviwopy.glm.vec4(1, 1, 1, 0.4)
        volumeSlice.sliceAxis.value = 3
        volumeSlice.planeNormal.value = inviwopy.glm.vec3(1, 0, 0)
        raycaster.positionindicator.enable.value = False

        meshCreator.meshType.selectedDisplayName = 'Plane'
        # meshCreator.scale.value = scaling_factor
        hfRender.heightScale.value = 0
        hfRender.terrainShadingMode.selectedDisplayName = 'Color Texture'
        hfRender.lighting.shadingMode.selectedDisplayName = 'No Shading'

        sliceCanvas.inputSize.dimensions.value = inviwopy.glm.size2_t(500, 500)
        volumeCanvas.inputSize.dimensions.value = inviwopy.glm.size2_t(500, 500)

        self.image_outport = raycaster.getOutport('outport')
        self.decoration_outport = hfRender.getOutport('image')
        self.volume_outport = hdf5Volume.getOutport('outport')

        if self.is_multichannel:
            self.decoration_inport = isoRaycaster.getInport('bg')
            self.transfer_function_prop = getattr(raycaster, 'transfer-functions').transferFunction1
        else:
            self.decoration_inport = meshRenderer.getInport('imageInport')
            self.transfer_function_prop = raycaster.isotfComposite.tf
        self.camera_prop = meshRenderer.camera

        meshRenderer.camera.fov.minValue = 5
        meshRenderer.camera.fov.value = 7
        meshRenderer.camera.farPlane = 500
        meshRenderer.camera.nearPlane = 1
