from pxr import Usd, UsdGeom, Sdf
import omni.usd
import omni.ui as ui
import omni.ext

class FindReplaceExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        self._window = ui.Window("Find and Replace", width=300, height=200)
        self._build_ui()
        
    def on_shutdown(self):
        self._window = None

    def _build_ui(self):
        with self._window.frame:
            with ui.VStack():
                # Input fields for dynamic variables
                self.default_prim_path = ui.StringField(label="Default Prim Path", height=30)
                self.default_prim_path.model.set_value("/Root")

                self.assembly_path = ui.StringField(label="Assembly Subprim Path", height=30)
                self.assembly_path.model.set_value("/SketchUp")

                self.prefix = ui.StringField(label="Prefix to Find", height=30)
                self.prefix.model.set_value("Ex_DecTree")

                self.reference_path = ui.StringField(label="Reference Target Path", height=30)
                self.reference_path.model.set_value("/Root/MasterTrees/Tree1")

                # Button to execute the function
                ui.Button("Run Find and Replace", clicked_fn=self._run_find_replace)

    def _run_find_replace(self):
        # Get input values from UI fields
        default_prim_path = self.default_prim_path.model.get_value_as_string()
        assembly_path = f"{default_prim_path}{self.assembly_path.model.get_value_as_string()}"
        xform_prefix = self.prefix.model.get_value_as_string()
        reference_target_path = self.reference_path.model.get_value_as_string()
        
        # Run the find and replace process
        stage = omni.usd.get_context().get_stage()
        if stage:
            self.process_xforms(stage, assembly_path, xform_prefix, reference_target_path)
        else:
            print("No currently open stage found.")

    def deactivate_children_and_add_reference_with_new_prim(self, prim, reference_path):
        # Deactivate all children
        for child in prim.GetAllChildren():
            child.SetActive(False)
        
        # Add a new empty prim under the given prim with a unique name
        new_prim_name = "ReferencePrim"
        new_prim_path = prim.GetPath().AppendChild(new_prim_name)
        new_prim = UsdGeom.Xform.Define(prim.GetStage(), new_prim_path)
        print(f"Xform Added at {new_prim_path}")
        
        # Add an internal reference to the new prim
        new_prim.GetPrim().GetReferences().AddInternalReference(reference_path)

    def process_xforms(self, stage, assembly_path, prefix, reference_path):
        """
        Process xforms under a specified assembly that match a given prefix.
        """
        assembly_prim = stage.GetPrimAtPath(assembly_path)
        if not assembly_prim:
            print(f"Assembly {assembly_path} not found.")
            return

        # Initialize the counter
        processed_count = 0

        for child in assembly_prim.GetAllChildren():
            if child.GetName().startswith(prefix):
                self.deactivate_children_and_add_reference_with_new_prim(child, reference_path)
                print(f"Processed {child.GetPath()}")
                processed_count += 1  # Increment the counter

        # Report the number of prims processed
        print(f"Total prims processed: {processed_count}")
