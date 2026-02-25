import math
def make_ciruclar_svg(filename,image_path,primitive_data,radius_step,total_arc_per_circle,angle_step,image_height,image_width):
    
    padding=20
    with open(filename, 'w') as f:
        # SVG Header
        canvas_w = image_width + padding + 20
        canvas_h = image_height + padding + 20

        f.write(
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="100%" height="100%" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" '
            f'preserveAspectRatio="xMidYMid meet">\n'
        )

        # f.write(f'<image href="../{image_path}" x="{padding}" y="{padding}" width="{image_width}" height="{image_height}" />')
        
        for index in range(1,len(primitive_data)):
            center_x=primitive_data[index]["center_x"]
            center_y=primitive_data[index]["center_y"]
            total_circles=math.ceil((10+primitive_data[index]["radius"])/radius_step)
            # # Add concentric circles
            for i in range(1, total_circles + 1):
                r = i * radius_step
                f.write(f'  <circle cx="{center_x+padding}" cy="{center_y+padding}" r="{r}" stroke="green" fill="none" stroke-width="0.5" stroke-opacity="0.5"/>\n')
        
            for j in range(total_arc_per_circle):
                curr_angle=j*angle_step
                curr_angle_radian=math.radians(curr_angle)
                x=center_x+padding+total_circles*radius_step*math.cos(curr_angle_radian)
                y=center_y+padding+total_circles*radius_step*math.sin(curr_angle_radian)
                f.write(f'<line x1="{center_x+padding}" y1="{center_y+padding}" x2="{x}" y2="{y}" stroke="green" stroke-width="0.5" stroke-opacity="0.5"/>')
            
      
      
            # SVG Footer
            myfile = open(f'temp/primitive_ciruclar_cover/primitive_{index}.txt', 'r')
            while True:
                line=myfile.readline()
                if not line:
                    break
                x_str, y_str = line.strip().split()
                first_x, first_y = int(x_str), int(y_str)
                first_radius=first_x*radius_step+radius_step
                first_angle=first_y*angle_step
                first_angle_radian=math.radians(first_angle)
                fx=center_x+padding+first_radius*math.cos(first_angle_radian)
                fy=center_y+padding+first_radius*math.sin(first_angle_radian)

                line=myfile.readline()
                if not line:
                    break
                x_str, y_str = line.strip().split()
                second_x, second_y = int(x_str), int(y_str)
                second_radius=second_x*radius_step+radius_step
                second_angle=second_y*angle_step
                second_angle_radian=math.radians(second_angle)
                sx=center_x+padding+second_radius*math.cos(second_angle_radian)
                sy=center_y+padding+second_radius*math.sin(second_angle_radian)

                while True:
                    if first_x!=second_x:
                        f.write(f'<line x1="{fx}" y1="{fy}" x2="{sx}" y2="{sy}" stroke="red" stroke-width="2"/>')
                        pass
                    else :
                        outwards=1
                        if first_y>second_y: outwards=0
                        if first_y==total_arc_per_circle-1 and second_y==0: outwards=1
                        if first_y==0 and second_y==total_arc_per_circle-1: outwards=0
                        f.write(f'<path d="M{fx} {fy} A{second_radius} {second_radius} 0 0 {outwards} {sx} {sy}" stroke="red" stroke-width="2" fill="none" />')
                    fx=sx
                    fy=sy
                    first_x=second_x
                    first_y=second_y
                    line=myfile.readline()
                    if not line:
                        break
                    x_str, y_str = line.strip().split()
                    second_x, second_y = int(x_str), int(y_str)
                    if second_x==-2 and second_y==-2 : break
                    second_radius=second_x*radius_step+radius_step
                    second_angle=second_y*angle_step
                    second_angle_radian=math.radians(second_angle)
                    sx=center_x+padding+second_radius*math.cos(second_angle_radian)
                    sy=center_y+padding+second_radius*math.sin(second_angle_radian)
                    

            
        myfile.close()


        f.write('</svg>\n')

    pass