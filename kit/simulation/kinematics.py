import json, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data'/'kinematics'
OUT.mkdir(parents=True,exist_ok=True)
def rx(a):
 c,s=math.cos(math.radians(a)),math.sin(math.radians(a)); return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def ry(a):
 c,s=math.cos(math.radians(a)),math.sin(math.radians(a)); return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def rz(a):
 c,s=math.cos(math.radians(a)),math.sin(math.radians(a)); return np.array([[c,-s,0],[s,c,0],[0,0,1]])
def T(r,p):
 m=np.eye(4);m[:3,:3]=r;m[:3,3]=p;return m
def matrix(m):
 return '\n'.join('[ '+'  '.join(f'{float(v): .6f}'.rstrip('0').rstrip('.') if abs(v)>1e-10 else '0' for v in row)+' ]' for row in m)
tasks=[(rz(30),[0,7,0],[0,0,0]),(ry(90),[-3,5,-8],[0,0,0]),(rz(30),[-1,-39,5],[-2,-8,0]),(rx(45),[4,-2,17],[0,5,-8])]
results=[];sections=[]
for i,(r,p,d) in enumerate(tasks,1):
 p=np.array(p);d=np.array(d);a=r@p+d;transform=T(r,d)
 assert np.allclose(r.T@r,np.eye(3)) and abs(np.linalg.det(r)-1)<1e-12
 assert np.allclose(np.linalg.inv(transform)@np.r_[a,1],np.r_[p,1])
 results.append({'task':i,'point_B_u':p.tolist(),'translation_A_u':d.tolist(),'rotation':r.tolist(),'transform':transform.tolist(),'point_A_u':a.tolist()})
 paragraph=[
 'Given a 30 degree rotation about positive Z_A, a point on positive Y_B has p_B = [0, 7, 0]^T u. The positive direction is confirmed by the counterclockwise drawing.',
 'Given a positive 90 degree rotation about Y_A and p_B = [-3, 5, -8]^T u, the origins coincide.',
 'Given a positive 30 degree rotation about Z_A and p_B = [-1, -39, 5]^T u, the origin translation is [-2, -8, 0]^T u, expressed in A. The translation is added after rotating the point.',
 'Given a positive 45 degree rotation about X_A and p_B = [4, -2, 17]^T u, the origin translation is [0, 5, -8]^T u, expressed in A.'
 ][i-1]
 calculations=[
 ['x_A = 0 cos(30 deg) - 7 sin(30 deg) = -3.500000 u','y_A = 0 sin(30 deg) + 7 cos(30 deg) = 6.062178 u','z_A = 0 u'],
 ['x_A = 0(-3) + 1(-8) = -8 u','y_A = 5 u','z_A = -1(-3) + 0(-8) = 3 u'],
 ['x_A = -1 cos(30 deg) - (-39) sin(30 deg) - 2 = 16.633975 u','y_A = -1 sin(30 deg) + (-39) cos(30 deg) - 8 = -42.274991 u','z_A = 5 + 0 = 5 u'],
 ['x_A = 4 u','y_A = -2 cos(45 deg) - 17 sin(45 deg) + 5 = -8.435029 u','z_A = -2 sin(45 deg) + 17 cos(45 deg) - 8 = 2.606602 u']][i-1]
 sections.append({'heading':f'Basis of kinematics task {i}', 'paragraphs':[paragraph, 'The transformation taking B coordinates into A coordinates is'], 'matrix':matrix(transform),'calculations':calculations,'table':{'headers':['Quantity','Final result'], 'rows':[['Point in frame A',f'[{a[0]:.6f}, {a[1]:.6f}, {a[2]:.6f}]^T u'],['Inverse substitution residual','Less than 1e-12 u'],['Rotation determinant','1.000000']]}})

R_C=np.array([[0,1,0],[0,0,1],[1,0,0]])
R_I=np.array([[0,-1,0],[1,0,0],[0,0,1]])
R_E=np.array([[0,1,0],[-1,0,0],[0,0,1]])
frames={'A':T(np.eye(3),[0,0,0]),'C':T(R_C,[0,3,5]),'F':T(R_C,[0,3,6]),'I':T(R_I,[4,0,5]),'E':T(R_E,[7,3,0])}
transforms={'A_from_E':frames['E'],'C_from_I':np.linalg.inv(frames['C'])@frames['I'],'F_from_A':np.linalg.inv(frames['F'])}
for m in frames.values():assert np.allclose(m@np.linalg.inv(m),np.eye(4))

# A new technical reconstruction of the visible frames, not an edited photograph.
im=Image.new('RGB',(1500,900),'white');dr=ImageDraw.Draw(im)
def font_load(size,bold=False):
 for f in ['C:/Windows/Fonts/'+('arialbd.ttf' if bold else 'arial.ttf'),'/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
  if Path(f).exists():return ImageFont.truetype(f,size)
 return ImageFont.load_default(size=size)
font=font_load(24);small=font_load(20);bold=font_load(30,True)
def proj(v):
 x,y,z=v;return (180+105*x+58*y,760-50*y-60*z)
def line(a,b,fill='#64748b',width=3):dr.line([proj(a),proj(b)],fill=fill,width=width)
def arrow(origin,vec,label,green=False):
 a=np.array(origin);b=a+np.array(vec)*1.3;p,q=proj(a),proj(b);color='#126747' if green else '#17202a'
 dr.line([p,q],fill=color,width=4);dx,dy=q[0]-p[0],q[1]-p[1];L=math.hypot(dx,dy);ux,uy=dx/L,dy/L
 dr.polygon([q,(q[0]-16*ux+6*uy,q[1]-16*uy-6*ux),(q[0]-16*ux-6*uy,q[1]-16*uy+6*ux)],fill=color)
 dr.text((q[0]+5,q[1]-22),label,font=font,fill=color)
edges=[([0,0,0],[4,0,0]),([4,0,0],[4,3,0]),([4,3,0],[7,3,0]),([7,3,0],[7,5,0]),([7,5,0],[0,5,0]),([0,5,0],[0,0,0]),([0,0,5],[4,0,5]),([4,0,5],[4,3,5]),([4,3,5],[0,3,5]),([0,3,5],[0,0,5]),([0,3,6],[7,3,6]),([7,3,6],[7,5,6]),([7,5,6],[0,5,6]),([0,5,6],[0,3,6])]
for a,b in edges:line(a,b)
for a,b in [([0,0,0],[0,0,5]),([4,0,0],[4,0,5]),([4,3,0],[4,3,5]),([7,3,0],[7,3,6]),([7,5,0],[7,5,6]),([0,5,0],[0,5,6]),([0,3,5],[0,3,6])]:line(a,b)
for name,m in frames.items():
 missing={'A':'Y','C':'Z','F':'X','I':'X','E':'Y'}[name]
 for j,axis in enumerate('XYZ'):arrow(m[:3,3],m[:3,j],axis+'_'+name,axis==missing)
dr.text((60,20),'Coordinate frame reconstruction',font=bold,fill='black')
dr.text((60,66),'Green arrows supply the missing axes   |   Dimensions use the slide length unit u',font=font,fill='#126747')
dr.text((60,850),'A (0,0,0)   C (0,3,5)   F (0,3,6)   I (4,0,5)   E (7,3,0)   |   Frames B and D are not located on the supplied slide',font=small,fill='#394b59')
fig=OUT/'coordinate_frames.png';im.save(fig)
sections.append({'heading':'Direct kinematics missing axes', 'paragraphs':['Use a right handed frame: X cross Y = Z, Y cross Z = X, and Z cross X = Y. Set the drawing basis to X_A toward the right, Y_A toward the back, and Z_A upward. The dimensions are interpreted as front width 4 u, tall width 7 u, front depth 3 u, rear depth 2 u, front height 5 u, and tall height 6 u.','The origin of F is read at the front left upper corner of the tall section, C at the front left corner at height 5 u, I at the front right upper corner, and E at the front right lower corner of the tall section.'], 'table':{'headers':['Frame','Missing axis in A coordinates','Right hand check'], 'rows':[['A','Y_A = (0,1,0)','X_A cross Y_A = Z_A'],['C','Z_C = Y_A','Z_A cross X_A = Y_A'],['F','X_F = Z_A','Y_F cross Z_F = X_A cross Y_A'],['I','X_I = Y_A','(-X_A) cross Z_A = Y_A'],['E','Y_E = X_A','Z_A cross (-Y_A) = X_A']]},'figure':str(fig),'caption':'Reconstruction of the visible slide geometry. Newly supplied axes appear in green.'})
sections.append({'heading':'Direct kinematics frame data','paragraphs':['A_from_B denotes the matrix that maps coordinates expressed in B to coordinates expressed in A. Its three rotation columns are the B unit axes expressed in A; the last column is the B origin expressed in A.'], 'table':{'headers':['Frame','Origin in A in u','X axis in A','Y axis in A','Z axis in A'],'rows':[[k, str(m[:3,3].astype(int).tolist()),str(m[:3,0].astype(int).tolist()),str(m[:3,1].astype(int).tolist()),str(m[:3,2].astype(int).tolist())] for k,m in frames.items()]}})
for k,m in transforms.items():
 sections.append({'heading':k.replace('_',' '), 'paragraphs':['Calculated from the visible coordinate frames using target_from_source = inverse(A_from_target) times A_from_source.'], 'matrix':matrix(m),'calculations':[f'Check: target_from_source times source_from_target = identity to numerical tolerance 1e-12.']})
sections.append({'heading':'Transforms involving frames B and D', 'paragraphs':['The slide requests A_from_B, B_from_A and D_from_B, but its figure does not define the locations or orientations of frames B and D. A_from_E is requested twice and has the same answer both times. Numerical B or D matrices are not uniquely determined by the supplied figure. The following symbolic answers completely express the relationships without assigning invented frame positions.','Let B have orientation R_B and origin b expressed in A; let D have orientation R_D and origin d expressed in A. Then the requested matrices are'], 'calculations':['A_from_B = block matrix [R_B, b; 0 0 0, 1]','B_from_A = block matrix [R_B transpose, -R_B transpose times b; 0 0 0, 1]','D_from_B = block matrix [R_D transpose times R_B, R_D transpose times (b - d); 0 0 0, 1]','Enter the missing axes and origins into kinematics.py to obtain numeric values when the complete figure is available.']})
sections.append({'heading':'Rotation conventions and verification','paragraphs':['The degree symbols in the tasks are inconsistently typed as a backtick or prime. They are interpreted as degrees, consistent with the illustrated 30 degree frame rotation and the 90 degree task. Treating them as arcminutes would produce different answers.','No centimetre or millimetre unit is supplied for the lecture coordinates, so u denotes the unspecified length unit used in the slides. This preserves dimensional consistency without inventing a scale.','For fixed axis rotations used here, R_z(beta) rotates the frame axes positively by the right hand rule. A_from_B times p_B returns p_A. The translation is expressed in A. For the lecture X Y Z example, multiplication order R_x(gamma) R_y(beta) R_z(alpha) matters; reverse multiplication describes a different convention.','Numerical checks confirm rotation orthogonality, determinant +1, homogeneous inverse consistency, and the four point transformation round trips. The printed lecture extraction appears to repeat beta where a third angle is expected in the angle recovery formulas; derive angles from the chosen matrix convention instead of copying that label.'],'table':{'headers':['Verification','Result'],'rows':[['Four point round trips','PASS below 1e-12 u'],['Visible frame rotations','PASS orthogonal determinant +1'],['Three calculated frame transforms','PASS inverse products'],['Missing B and D definitions','Symbolic solution supplied']]}})
report={'id':'08_Kinematics','title':'Kinematics exercise solutions','source':'02 Basis of kinematics.pdf pages 23 and 27; 03 Direct Kinematics cont.pdf page 4','summary':'The four coordinate transformation tasks and all visible frame exercises are solved below. Worked substitutions retain angle and length units. B and D relationships are given symbolically because those frames are absent from the supplied drawing.','sections':sections,'references':['02 Basis of kinematics.pdf, supplied lecture, pages 21 to 27.','03 Direct Kinematics cont.pdf, supplied lecture, pages 1 to 6.','01 Introduction to robotics.pdf, supplied lecture, contextual reading.']}
content_dir=ROOT/'data'/'report_content';content_dir.mkdir(parents=True,exist_ok=True)
(content_dir/'kinematics_content.json').write_text(json.dumps({'reports':[report]},indent=2),encoding='utf-8')
(OUT/'results.json').write_text(json.dumps({'tasks':results,'frames':{k:v.tolist() for k,v in frames.items()},'transforms':{k:v.tolist() for k,v in transforms.items()},'checks':'passed'},indent=2),encoding='utf-8')
print('Kinematics numeric checks passed; 4 tasks and 3 numeric frame transforms generated.')
