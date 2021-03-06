#  ENVISIoN
#
#  Copyright (c) 2020-2021 Amanda Aasa, Amanda Svennblad, Gabriel Anderberg, Didrik Axén,
#  Adam Engman, Kristoffer Gubberud Maras, Joakim Stenborg
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##############################################################################################
#  Alterations to this file by Gabriel Anderberg, Didrik Axén,
#  Adam Engman, Kristoffer Gubberud Maras, Joakim Stenborg
#
#  To the extent possible under law, the person who associated CC0 with
#  the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
#
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.



# Name: Bandstructure3DNetworkHandler
import sys,os,inspect
import inviwopy as ivw
import inviwopy.glm as glm
import h5py
import numpy as np
import time

from envisionpy.processor_network.NetworkHandler import NetworkHandler

class Bandstructure3DNetworkHandler(NetworkHandler):
    def __init__(self, hdf5_path, inviwoApp):
        NetworkHandler.__init__(self, inviwoApp)
        self.canvas = 0
        self.processors = {}
        self.setup_bandstructure_network(hdf5_path)



    @staticmethod
    def valid_hdf5(hdf5_file):
        return hdf5_file.get("BandStructure") != None

    def processorInfo():
        return ivw.ProcessorInfo(
            classIdentifier = "org.inviwo.Bandstructure3DNetworkHandler",
            displayName = "Bandstructure3DNetworkHandler",
            category = "Python",
            codeState = ivw.CodeState.Stable,
            tags = ivw.Tags.PY
        )

    def stop_vis(self, vis_type = None):
        self.hide()
        #for processor in self.network.processors:
        #        self.network.removeProcessor(processor)


    def get_ui_data(self):
        return [
            "bandstructure3d"
            ]

    def show(self):
        #canvas = self.network.getProcessor(canvas)
        self.canvas.widget.show()


    def hide(self):
        #canvas = self.network.getProcessor('org.inviwo.CanvasGL')
        self.canvas.widget.hide()


    def getProcessorInfo(self):
        return Bandstructure3DNetworkHandler.processorInfo()

    def initializeResources(self):
        print("init")

    def setup_bandstructure_network(self, h5file):
        self.factory = self.app.processorFactory
        #Extractiong network metadata
        with h5py.File(h5file, 'r') as f:
            KPoints = f.get('BandStructure').get('KPoints')[()]
            Symbols = f.get('Highcoordinates')
            length_iteration = len(KPoints)#number of iterations
            sym_list = []
            kpoint_list = []
            iteration_list = []
            sym_it_list = []

            for x in range(len(Symbols)):
                symbol = f.get('Highcoordinates').get(str(x)).get('Symbol')[()]
                koord = f.get('Highcoordinates').get(str(x)).get('Coordinates')[()]
                sym_list.append(
                    symbol
                )
                kpoint_list.append(
                    koord
                )

                for i in range(len(KPoints)):
                    if np.array_equal(KPoints[i],kpoint_list[x]):
                        iteration_list.append(i)
                        sym_it_list.append(symbol)

            for l in range(len(iteration_list)-1):
                for j in range(0, len(iteration_list)-l-1):
                    if iteration_list[j] > iteration_list[j+1]:
                        iteration_list[j], iteration_list[j+1] = iteration_list[j+1], iteration_list[j]
                        sym_it_list[j], sym_it_list[j+1] = sym_it_list[j+1], sym_it_list[j]


        #HDF5Source
        hdf5_source = self.factory.create('org.inviwo.hdf5.Source', glm.ivec2(0, 0))
        hdf5_source.identifier = 'hdf5 source'
        hdf5_source.filename.value = h5file
        self.network.addProcessor(hdf5_source)


        #HDF5PathSelection
        hdf5_path_selection = self.factory.create('org.inviwo.hdf5.PathSelection', glm.ivec2(0,75))
        hdf5_path_selection.identifier = 'band'
        hdf5_path_selection.selection.value = '/Bandstructure/Bands'
        self.network.addProcessor(hdf5_path_selection)

        self.network.addConnection(
            hdf5_source.getOutport('outport'),
            hdf5_path_selection.getInport('inport')
        )

        #HDF5PathSelectionAllChildren
        hdf5_path_selection_all_children = self.factory.create('org.inviwo.HDF5PathSelectionAllChildren', glm.ivec2(0,150))
        hdf5_path_selection_all_children.identifier = 'All'
        self.network.addProcessor(hdf5_path_selection_all_children)

        self.network.addConnection(
            hdf5_path_selection.getOutport('outport'),
            hdf5_path_selection_all_children.getInport('hdf5HandleInport')
        )


        #HDF5ToFunction, denna funkar inte för tillfället
        hdf5_to_function = self.factory.create('org.inviwo.HDF5ToFunction', glm.ivec2(0, 225))
        hdf5_to_function.identifier = 'Convert to function'
        self.network.addProcessor(hdf5_to_function)

        self.network.addConnection(
            hdf5_path_selection_all_children.getOutport('hdf5HandleVectorOutport'),
            hdf5_to_function.getInport('hdf5HandleFlatMultiInport')
        )

#FunctionToDataframe
        function_to_dataframe = self.factory.create('org.inviwo.FunctionToDataFrame',glm.ivec2(0,300))
        function_to_dataframe.identifier = 'Function to dataframe'
        self.network.addProcessor(function_to_dataframe)

        self.network.addConnection(
            hdf5_to_function.getOutport('functionVectorOutport'),
            function_to_dataframe.getInport('functionFlatMultiInport')
        )

#LinePlot
        line_plot = self.factory.create('org.inviwo.LinePlotProcessor',glm.ivec2(0,375))
        line_plot.identifier = 'Line Plot'
        line_plot.getPropertyByIdentifier('allYSelection').value = True
        line_plot.getPropertyByIdentifier('enable_line').value = True
        line_plot.getPropertyByIdentifier('show_x_labels').value = False
        self.network.addProcessor(line_plot)

        self.network.addConnection(
            function_to_dataframe.getOutport('dataframeOutport'),
            line_plot.getInport('dataFrameInport')
        )


#2DMeshRenderer
        mesh_render = self.factory.create('org.inviwo.Mesh2DRenderProcessorGL', glm.ivec2(0,450))
        mesh_render.identifier = 'Render'
        self.network.addProcessor(mesh_render)

        self.network.addConnection(
            line_plot.getOutport('outport'),
            mesh_render.getInport('inputMesh')
        )
        self.network.addConnection(
            line_plot.getOutport('labels'),
            mesh_render.getInport('imageInport')
        )


#Background
        background = self.factory.create('org.inviwo.Background',glm.ivec2(0,525))
        background.identifier = 'Background'
        self.network.addProcessor(background)

        background.bgColor1.value = ivw.glm.vec4(1)
        background.bgColor2.value = ivw.glm.vec4(1)

        self.network.addConnection(
            mesh_render.getOutport('outputImage'),
            background.getInport('inport')
        )

#TextOverlay
        text_overlay = self.factory.create('org.inviwo.TextOverlayGL',glm.ivec2(0,600))
        text_overlay.identifier = 'Text overlay GL'
        self.network.addProcessor(text_overlay)

        text_overlay.font.fontSize.value = 20
        text_overlay.position.value = ivw.glm.vec2(0.43, 0.93)
        text_overlay.color.value = ivw.glm.vec4(0,0,0,1)
        text_overlay.text.value = 'Energy [eV]'

        self.network.addConnection(
            background.getOutport('outport'),
            text_overlay.getInport('inport')
        )

#SecondTextOverlay
        second_text_overlay = self.factory.create('org.inviwo.TextOverlayGL',glm.ivec2(0,675))
        second_text_overlay.identifier = 'Text overlay GL'
        self.network.addProcessor(second_text_overlay)

        second_text_overlay.font.fontSize.value = 20
        second_text_overlay.position.value = ivw.glm.vec2(0.35, 0.02)
        second_text_overlay.color.value = ivw.glm.vec4(0,0,0,1)
        second_text_overlay.text.value = 'Critical points in the brillouin zone'

        self.network.addConnection(
            text_overlay.getOutport('outport'),
            second_text_overlay.getInport('inport')
        )


#DrawSymbols
        overlay_list = []
        mul_iteration = 0.8/len(KPoints)
        k = 0
        new_iteration_list = []
        print(len(sym_it_list))
        for q in range(len(sym_it_list)):
            if k != len(sym_it_list)-1:
                k = k+1
                if not np.array_equal(sym_it_list[q],sym_it_list[k]):
                    third_text_overlay = self.factory.create('org.inviwo.TextOverlayGL',glm.ivec2(200*q,750))
                    self.network.addProcessor(third_text_overlay)
                    third_text_overlay.font.fontSize.value = 20
                    x_cor = (mul_iteration*iteration_list[q]) + 0.1
                    third_text_overlay.position.value = ivw.glm.vec2(x_cor, 0.06)
                    third_text_overlay.color.value = ivw.glm.vec4(0,0,0,1)
                    third_text_overlay.text.value = sym_it_list[q]
                    overlay_list.append(third_text_overlay)
                    new_iteration_list.append(iteration_list[q])
            elif k == len(sym_it_list)-1:
                if not np.array_equal(sym_it_list[q],sym_it_list[q-1]):
                    third_text_overlay = self.factory.create('org.inviwo.TextOverlayGL',glm.ivec2(200*q,750))
                    self.network.addProcessor(third_text_overlay)
                    third_text_overlay.font.fontSize.value = 20
                    x_cor = (mul_iteration*iteration_list[q]) + 0.1
                    third_text_overlay.position.value = ivw.glm.vec2(x_cor, 0.06)
                    third_text_overlay.color.value = ivw.glm.vec4(0,0,0,1)
                    third_text_overlay.text.value = sym_it_list[q]
                    overlay_list.append(third_text_overlay)
                    new_iteration_list.append(iteration_list[q])

        self.network.addConnection(
            second_text_overlay.getOutport('outport'),
            overlay_list[0].getInport('inport')
        )

        for w in range(1,(len(overlay_list))-1):
            self.network.addConnection(
               overlay_list[w-1].getOutport('outport'),
               overlay_list[w].getInport('inport')
            )
            self.network.addConnection(
                overlay_list[w].getOutport('outport'),
                overlay_list[w+1].getInport('inport')
            )




#DrawLinesToEverySymbol
        line_list = []

        for r in range(0, len(new_iteration_list)):
            line_plot = self.factory.create('org.inviwo.LinePlotProcessor',glm.ivec2(200*r,375))
            line_plot.getPropertyByIdentifier('allYSelection').value = True
            line_plot.getPropertyByIdentifier('enable_line').value = True
            line_plot.getPropertyByIdentifier('line_x_coordinate').minValue = 0
            line_plot.getPropertyByIdentifier('line_x_coordinate').maxValue = length_iteration
            self.network.addProcessor(line_plot)
            line_plot.getPropertyByIdentifier('line_x_coordinate').value = new_iteration_list[r]
            line_list.append(line_plot)
            self.network.addConnection(
                function_to_dataframe.getOutport('dataframeOutport'),
                line_list[r].getInport('dataFrameInport')
            )
            self.network.addConnection(
                line_plot.getOutport('outport'),
                mesh_render.getInport('inputMesh')
            )


#Canvas
        canvas = self.factory.create('org.inviwo.CanvasGL', glm.ivec2(0,825))
        canvas.identifier = 'Canvas'
        self.canvas = canvas
        self.network.addProcessor(canvas)

        self.network.addConnection(
            third_text_overlay.getOutport('outport'),
            canvas.getInport('inport')
        )



        canvas.inputSize.dimensions.value = ivw.glm.size2_t(900,825)

        canvas.widget.show()

        hdf5_path_selection.selection.value = '/Bandstructure/Bands'
