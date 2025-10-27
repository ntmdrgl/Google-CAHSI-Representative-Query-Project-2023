# -*- coding: utf-8 -*-
"""
Created on March 11, 2024
Authors: Alexander Madrigal, Nathaniel Madrigal

"""
from sqlalchemy.ext.automap import automap_base
from sqlalchemy_schemadisplay import create_schema_graph

# Import your SQLAlchemy models from the generated models.py file
from models import Base

# Create a Base class for reflection
Base.prepare(engine, reflect=True)

# Create a graph using SQLAlchemy models
graph = create_schema_graph(metadata=Base.metadata)

# Save the graph as an image
graph.write_png('database_schema.png')

