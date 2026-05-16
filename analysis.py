import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import griddata
import sys
import json
import os

def calculate_rho_and_coords(row):
    """
    استخراج 8 نقطه داده از هر سطر CSV شامل محاسبه مختصات فضایی (X, Y, Z) و مقاومت ویژه (Rho)
    """
    points = []
    
    # محور Y بر اساس شماره خط و فاصله بین خطوط
    y = row['Line_Num'] * row['Line_Spacing']
    
    # جریان‌های دو فاز (تبدیل از میلی‌آمپر به آمپر)
    i_e1 = abs(row['I_E1_mA']) / 1000.0 if row['I_E1_mA'] != 0 else 0.001
    i_e2 = abs(row['I_E2_mA']) / 1000.0 if row['I_E2_mA'] != 0 else 0.001

    # --- فاز 1: تزریق از E1
    receivers_e1 = ['A', 'B', 'C', 'D']
    for rx in receivers_e1:
        dist_cm = row[f'd_E1_{rx}']
        v_mv = abs(row[f'V_E1_{rx}'])
        
        a_spacing = dist_cm / 100.0
        
        if a_spacing > 0:
            r = (v_mv / 1000.0) / i_e1
            k = 2 * np.pi * a_spacing
            rho = r * k
            
            x = a_spacing / 2.0
            z = - (a_spacing / 2.0)
            
            points.append((x, y, z, rho))

    # --- فاز 2: تزریق از E2
    receivers_e2 = ['A', 'B', 'C', 'D']
    for rx in receivers_e2:
        dist_cm = row[f'd_E2_{rx}']
        v_mv = abs(row[f'V_E2_{rx}'])
        
        a_spacing = dist_cm / 100.0
        
        if a_spacing > 0:
            r = (v_mv / 1000.0) / i_e2
            k = 2 * np.pi * a_spacing
            rho = r * k
            
            x = 4.0 - (a_spacing / 2.0)
            z = - (a_spacing / 2.0)
            
            points.append((x, y, z, rho))
            
    return points


def plot_3d_volume_tomography(csv_file, output_file):
    """نمودار Volume Tomography"""
    print(f"📊 درحال محاسبه Volume Tomography...")
    
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"❌ خطا در خواندن فایل: {e}")
        return None

    all_data = []
    for _, row in df.iterrows():
        all_data.extend(calculate_rho_and_coords(row))

    if len(all_data) < 4:
        print("❌ داده کافی برای رسم نمودار وجود ندارد")
        return None

    data_array = np.array(all_data)
    X_pts = data_array[:, 0]
    Y_pts = data_array[:, 1]
    Z_pts = data_array[:, 2]
    Rho_vals = data_array[:, 3]

    print(f"✅ {len(Rho_vals)} نقطه اندازه‌گیری پردازش شد")

    grid_res = 40
    xi = np.linspace(min(X_pts)-0.5, max(X_pts)+0.5, grid_res)
    yi = np.linspace(min(Y_pts)-0.5, max(Y_pts)+0.5, grid_res)
    zi = np.linspace(min(Z_pts)-1.0, 0, grid_res)
    
    X, Y, Z = np.meshgrid(xi, yi, zi)

    V = griddata((X_pts, Y_pts, Z_pts), Rho_vals, (X, Y, Z), method='linear', fill_value=np.mean(Rho_vals))

    vmin, vmax = np.percentile(Rho_vals, 5), np.percentile(Rho_vals, 95)

    fig = go.Figure(data=go.Volume(
        x=X.flatten(),
        y=Y.flatten(),
        z=Z.flatten(),
        value=V.flatten(),
        isomin=vmin,
        isomax=vmax,
        opacity=0.15,
        surface_count=20,
        colorscale='Turbo',
        colorbar=dict(title='Apparent Resistivity (Ω·m)', thickness=20)
    ))

    fig.add_trace(go.Scatter3d(
        x=X_pts, y=Y_pts, z=Z_pts,
        mode='markers',
        marker=dict(size=4, color='black', symbol='diamond'),
        name='Sensors Data Points'
    ))

    fig.update_layout(
        title='GeoScanner Pro - 3D Volume Tomography',
        scene=dict(
            xaxis_title='Distance X (m)',
            yaxis_title='Line Y (m)',
            zaxis_title='Depth Z (m)',
            aspectmode='data',
            camera=dict(eye=dict(x=1.5, y=-1.5, z=0.5))
        ),
        template='plotly_white',
        margin=dict(l=0, r=0, b=0, t=50)
    )

    fig.write_html(output_file)
    print(f"✅ Volume Tomography ذخیره شد: {output_file}")
    return output_file


def plot_3d_gradient_tomography(csv_file, output_file):
    """نمودار Gradient Tomography"""
    print(f"📊 درحال محاسبه Gradient Tomography...")
    
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"❌ خطا در خواندن فایل: {e}")
        return None

    all_data = []
    for _, row in df.iterrows():
        all_data.extend(calculate_rho_and_coords(row))

    if len(all_data) < 4:
        print("❌ داده کافی برای رسم نمودار وجود ندارد")
        return None

    data_array = np.array(all_data)
    X_pts = data_array[:, 0]
    Y_pts = data_array[:, 1]
    Z_pts = data_array[:, 2]
    Rho_vals = data_array[:, 3]

    print(f"✅ {len(Rho_vals)} نقطه اندازه‌گیری پردازش شد")

    grid_res = 40
    xi = np.linspace(min(X_pts)-0.5, max(X_pts)+0.5, grid_res)
    yi = np.linspace(min(Y_pts)-0.5, max(Y_pts)+0.5, grid_res)
    zi = np.linspace(min(Z_pts)-1.0, 0, grid_res)
    X, Y, Z = np.meshgrid(xi, yi, zi)

    V_rho = griddata((X_pts, Y_pts, Z_pts), Rho_vals, (X, Y, Z), method='linear', fill_value=np.mean(Rho_vals))

    dV_dy, dV_dx, dV_dz = np.gradient(V_rho)
    gradient_magnitude = np.sqrt(dV_dx**2 + dV_dy**2 + dV_dz**2)

    vmin = np.percentile(gradient_magnitude, 60) 
    vmax = np.percentile(gradient_magnitude, 98)

    fig = go.Figure(data=go.Volume(
        x=X.flatten(),
        y=Y.flatten(),
        z=Z.flatten(),
        value=gradient_magnitude.flatten(),
        isomin=vmin,
        isomax=vmax,
        opacity=0.2,
        surface_count=20,
        colorscale='Jet',
        colorbar=dict(title='Gradient Intensity', thickness=20)
    ))

    fig.add_trace(go.Scatter3d(
        x=X_pts, y=Y_pts, z=Z_pts,
        mode='markers',
        marker=dict(size=3, color='black', opacity=0.5),
        name='Sensors'
    ))

    fig.update_layout(
        title='3D Tomography - Gradient Visualizer',
        scene=dict(xaxis_title='X (m)', yaxis_title='Line Y (m)', zaxis_title='Depth Z (m)'),
        template='plotly_white'
    )

    fig.write_html(output_file)
    print(f"✅ Gradient Tomography ذخیره شد: {output_file}")
    return output_file


def process_csv(csv_file, output_dir):
    """پردازش کامل فایل CSV و تولید هر دو نمودار"""
    os.makedirs(output_dir, exist_ok=True)
    
    volume_file = os.path.join(output_dir, "3D_Volume_Tomography.html")
    gradient_file = os.path.join(output_dir, "3D_Gradient_Tomography.html")
    
    try:
        vol_result = plot_3d_volume_tomography(csv_file, volume_file)
        grad_result = plot_3d_gradient_tomography(csv_file, gradient_file)
        
        result = {
            "status": "success",
            "volume_file": vol_result,
            "gradient_file": grad_result
        }
        print(json.dumps(result))
        return result
    except Exception as e:
        error_result = {
            "status": "error",
            "message": str(e)
        }
        print(json.dumps(error_result))
        return error_result


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"status": "error", "message": "Missing arguments"}))
        sys.exit(1)
    
    csv_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    process_csv(csv_file, output_dir)
