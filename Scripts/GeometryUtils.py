"""
Collection of helpers used to work with geometries in Clarisse.
"""

def get_transformed_bbox(item):
    """
    If item is a geometry object or a bundle (or a path to one of those), this function will return
    its transformed (taking any transformation into account, like translate, rotate, scale, etc.) bbox.
    If it isn't, it'll return None.
    """
    if type(item) == type(""):
        item = ix.get_item(item)

    if item is None:
        return None

    module = item.get_module()
    if module.is_kindof(ix.api.ModuleGeometry.class_info()) is False and module.is_kindof(ix.api.ModuleGeometryBundle.class_info()) is False:
        return None

    bbox = ix.api.GMathBbox3d()
    module.get_bbox().transform_bbox_and_get_bbox(module.get_global_matrix(), bbox)
    return bbox
