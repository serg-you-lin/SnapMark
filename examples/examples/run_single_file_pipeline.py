import snapmark as sm

# Pipeline su singolo file (una chiamata!)
seq = sm.SequenceBuilder().file_name().build()

sm.single_file_pipeline(
    "Examples/Input/F1.dxf",
    sm.Aligner(),
    sm.AddMark(seq, scale_factor=100),
    sm.AddX(sm.find_circle_by_radius(5, 10), x_size=5),
    use_backup=True
)


sm.single_file_pipeline(
    "Examples/Input/F2.dxf",
    sm.Aligner(),
    sm.AddMark(seq, scale_factor=100),
    sm.SubstituteCircle(sm.find_circle_by_radius(9, 12), new_diameter=20, layer="SUBSTITUTED"),
    use_backup=True
)



sm.single_file_pipeline(
    "Examples/Input/F3.dxf",
    sm.AddMark(seq, scale_factor=100),
    sm.RemoveCircle(sm.find_circle_by_radius(10, 15)),
    use_backup=True
)
