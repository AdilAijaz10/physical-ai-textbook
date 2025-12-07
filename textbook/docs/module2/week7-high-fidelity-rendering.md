---
sidebar_position: 2
---

# Week 7: High-fidelity Rendering in Unity

## Learning Objectives

By the end of this week, you will be able to:
- Set up Unity for robotics simulation with ROS integration
- Create photorealistic environments for humanoid robots
- Implement advanced rendering techniques (PBR, lighting, post-processing)
- Integrate Unity with ROS 2 for sensor simulation
- Optimize Unity scenes for real-time performance

## Introduction to Unity for Robotics

Unity is a powerful game engine that can be used for high-fidelity robotics simulation. Its advanced rendering capabilities, physics engine, and flexible scripting environment make it ideal for creating photorealistic environments and realistic sensor simulation for humanoid robots.

### Unity Robotics Ecosystem
- **Unity Robot Framework**: Pre-built components for robotics simulation
- **ROS#**: ROS/ROS 2 integration package
- **Unity Perception**: Tools for synthetic data generation
- **ML-Agents**: Reinforcement learning framework
- **Unity Physics**: Advanced physics simulation

## Setting Up Unity for Robotics

### Installing Unity Hub and Editor
1. Download Unity Hub from [Unity's website](https://unity.com/download)
2. Install Unity 2022.3 LTS or later
3. Create a new 3D project

### Installing ROS# Package
```bash
# In Unity Package Manager:
# Window -> Package Manager -> Add package from git URL
# Add: https://github.com/siemens/ros-sharp.git
```

### Alternative: Unity Robotics Hub
Unity provides a specialized distribution for robotics:
1. Download Unity Robotics Hub
2. Install with robotics packages pre-configured
3. Create new robotics project

## Basic Unity Scene Setup

### Creating a Robot Environment
1. **Create a new scene**:
   - File -> New Scene
   - Choose 3D template

2. **Set up coordinate system**:
   - Unity uses left-handed coordinate system (X: right, Y: up, Z: forward)
   - ROS uses right-handed coordinate system (X: forward, Y: left, Z: up)
   - Use conversion scripts for proper transformation

3. **Basic environment**:
```csharp
// RobotEnvironment.cs - Basic environment setup
using UnityEngine;

public class RobotEnvironment : MonoBehaviour
{
    [Header("Environment Settings")]
    public float gravity = -9.81f;
    public Color environmentColor = Color.grey;

    [Header("Lighting")]
    public Light mainLight;
    public float lightIntensity = 1.0f;

    void Start()
    {
        // Set gravity
        Physics.gravity = new Vector3(0, gravity, 0);

        // Set environment color
        RenderSettings.fogColor = environmentColor;

        // Configure main light
        if (mainLight != null)
        {
            mainLight.intensity = lightIntensity;
        }
    }
}
```

## Physics Configuration for Humanoid Robots

### Unity Physics vs ROS Physics
Unity uses its own physics engine, but for consistency with ROS, you may need to:
- Match physical properties (mass, friction, etc.)
- Synchronize coordinate systems
- Configure similar collision behaviors

### Configuring Rigidbodies for Robot Parts
```csharp
// RobotJoint.cs - Configure robot joint physics
using UnityEngine;

[RequireComponent(typeof(Rigidbody))]
public class RobotJoint : MonoBehaviour
{
    [Header("Joint Configuration")]
    public float jointMass = 1.0f;
    public float jointDrag = 0.1f;
    public float jointAngularDrag = 0.05f;
    public bool useGravity = true;
    public bool isKinematic = false;

    private Rigidbody rb;

    void Start()
    {
        rb = GetComponent<Rigidbody>();
        ConfigureRigidbody();
    }

    void ConfigureRigidbody()
    {
        rb.mass = jointMass;
        rb.drag = jointDrag;
        rb.angularDrag = jointAngularDrag;
        rb.useGravity = useGravity;
        rb.isKinematic = isKinematic;
    }

    public void SetJointLimits(float minAngle, float maxAngle)
    {
        // Unity doesn't have built-in joint limits like ROS
        // You'll need to implement custom joint constraints
    }
}
```

## Advanced Rendering Techniques

### Physically Based Rendering (PBR)
```csharp
// PBRMaterialManager.cs - Manage PBR materials
using UnityEngine;

public class PBRMaterialManager : MonoBehaviour
{
    [Header("Material Properties")]
    public Texture2D albedoMap;
    public Texture2D normalMap;
    public Texture2D metallicMap;
    public Texture2D roughnessMap;

    [Range(0, 1)] public float metallic = 0.5f;
    [Range(0, 1)] public float smoothness = 0.5f;

    public Material CreatePBRMaterial()
    {
        Material material = new Material(Shader.Find("Standard"));

        if (albedoMap != null) material.mainTexture = albedoMap;
        material.SetTexture("_BumpMap", normalMap);
        material.SetTexture("_MetallicGlossMap", metallicMap);
        material.SetTexture("_ParallaxMap", roughnessMap);

        material.SetFloat("_Metallic", metallic);
        material.SetFloat("_Glossiness", smoothness);

        return material;
    }
}
```

### Lighting Setup
```csharp
// AdvancedLighting.cs - Configure advanced lighting
using UnityEngine;
using UnityEngine.Rendering;

public class AdvancedLighting : MonoBehaviour
{
    [Header("Lighting Configuration")]
    public Light directionalLight;
    public bool enableShadows = true;
    public ShadowResolution shadowResolution = ShadowResolution.High;

    [Header("Post-Processing")]
    public bool enablePostProcessing = true;
    public float exposure = 0.0f;
    public float contrast = 1.0f;

    void Start()
    {
        SetupLighting();
        SetupPostProcessing();
    }

    void SetupLighting()
    {
        if (directionalLight != null)
        {
            directionalLight.shadows = enableShadows ? LightShadows.Soft : LightShadows.None;
            directionalLight.shadowResolution = shadowResolution;
            directionalLight.shadowStrength = 0.8f;
        }
    }

    void SetupPostProcessing()
    {
        if (enablePostProcessing)
        {
            // Configure post-processing effects
            // This requires Unity's Post-Processing package
        }
    }
}
```

## Sensor Simulation in Unity

### Camera Sensor Simulation
```csharp
// UnityCameraSensor.cs - Simulate RGB camera
using UnityEngine;
using System.Collections;
using System.IO;

public class UnityCameraSensor : MonoBehaviour
{
    [Header("Camera Settings")]
    public Camera sensorCamera;
    public int imageWidth = 640;
    public int imageHeight = 480;
    public float updateRate = 30.0f; // Hz

    [Header("Output Settings")]
    public string outputTopic = "/unity_camera/image_raw";
    public bool saveToDisk = false;
    public string savePath = "Assets/SensorData/";

    private RenderTexture renderTexture;
    private float updateInterval;
    private float lastUpdateTime;

    void Start()
    {
        SetupCamera();
        updateInterval = 1.0f / updateRate;
        lastUpdateTime = 0;
    }

    void SetupCamera()
    {
        if (sensorCamera == null)
            sensorCamera = GetComponent<Camera>();

        renderTexture = new RenderTexture(imageWidth, imageHeight, 24);
        sensorCamera.targetTexture = renderTexture;
    }

    void Update()
    {
        if (Time.time - lastUpdateTime >= updateInterval)
        {
            CaptureImage();
            lastUpdateTime = Time.time;
        }
    }

    void CaptureImage()
    {
        RenderTexture.active = renderTexture;
        Texture2D image = new Texture2D(imageWidth, imageHeight, TextureFormat.RGB24, false);
        image.ReadPixels(new Rect(0, 0, imageWidth, imageHeight), 0, 0);
        image.Apply();

        // Convert to ROS message format (implementation depends on ROS#)
        // Publish to ROS topic

        if (saveToDisk)
        {
            byte[] bytes = image.EncodeToPNG();
            string filename = Path.Combine(savePath, $"camera_{System.DateTime.Now:yyyyMMdd_HHmmss}.png");
            File.WriteAllBytes(filename, bytes);
        }

        Destroy(image);
    }
}
```

### LiDAR Simulation
```csharp
// UnityLidarSensor.cs - Simulate LiDAR sensor
using UnityEngine;
using System.Collections.Generic;

public class UnityLidarSensor : MonoBehaviour
{
    [Header("Lidar Configuration")]
    public int horizontalSamples = 720;
    public int verticalSamples = 1;
    public float minAngle = -90f; // degrees
    public float maxAngle = 90f;  // degrees
    public float maxRange = 10.0f;
    public float updateRate = 10.0f;

    [Header("Raycast Settings")]
    public LayerMask detectionMask = -1;
    public float noiseLevel = 0.01f;

    private float updateInterval;
    private float lastUpdateTime;
    private List<float> ranges;

    void Start()
    {
        updateInterval = 1.0f / updateRate;
        lastUpdateTime = 0;
        ranges = new List<float>(new float[horizontalSamples]);
    }

    void Update()
    {
        if (Time.time - lastUpdateTime >= updateInterval)
        {
            ScanEnvironment();
            lastUpdateTime = Time.time;
        }
    }

    void ScanEnvironment()
    {
        float angleIncrement = (maxAngle - minAngle) / horizontalSamples;

        for (int i = 0; i < horizontalSamples; i++)
        {
            float currentAngle = minAngle + (i * angleIncrement) * Mathf.Deg2Rad;

            Vector3 direction = new Vector3(
                Mathf.Cos(currentAngle),
                0,
                Mathf.Sin(currentAngle)
            );

            direction = transform.TransformDirection(direction);

            if (Physics.Raycast(transform.position, direction, out RaycastHit hit, maxRange, detectionMask))
            {
                float distance = hit.distance;
                // Add noise
                distance += Random.Range(-noiseLevel, noiseLevel) * distance;
                ranges[i] = distance;
            }
            else
            {
                ranges[i] = float.MaxValue; // No hit
            }
        }

        // Publish ranges to ROS topic
        PublishLidarData();
    }

    void PublishLidarData()
    {
        // Implementation depends on ROS# integration
        // Convert ranges to LaserScan message and publish
    }
}
```

## Unity-ROS Integration

### Setting Up ROS Connection
```csharp
// ROSConnectionManager.cs - Manage ROS connection
using UnityEngine;
using RosSharp.RosBridgeClient;

public class ROSConnectionManager : MonoBehaviour
{
    [Header("ROS Connection")]
    public string rosBridgeServerUrl = "ws://127.0.0.1:9090";
    public float connectionTimeout = 5.0f;

    private RosSocket rosSocket;

    void Start()
    {
        ConnectToROSBridge();
    }

    void ConnectToROSBridge()
    {
        RosBridgeClient.Protocols.WebSocketNetProtocol protocol =
            new RosBridgeClient.Protocols.WebSocketNetProtocol(rosBridgeServerUrl);

        rosSocket = new RosSocket(protocol, OnConnected, OnDisconnected);
    }

    void OnConnected()
    {
        Debug.Log("Connected to ROS Bridge");
        // Subscribe to topics, publish initial messages
    }

    void OnDisconnected()
    {
        Debug.Log("Disconnected from ROS Bridge");
        // Handle disconnection
    }

    void OnDestroy()
    {
        rosSocket?.Close();
    }
}
```

### Publishing Sensor Data to ROS
```csharp
// SensorPublisher.cs - Publish sensor data to ROS
using UnityEngine;
using RosSharp.RosBridgeClient;
using RosSharp.Messages.Sensor;

public class SensorPublisher : MonoBehaviour
{
    [Header("Topic Configuration")]
    public string imageTopic = "/unity_camera/image_raw";
    public string lidarTopic = "/unity_lidar/scan";
    public string imuTopic = "/unity_imu/data";

    private RosSocket rosSocket;
    private UnityCameraSensor cameraSensor;
    private UnityLidarSensor lidarSensor;

    void Start()
    {
        // Get references to sensor components
        cameraSensor = GetComponent<UnityCameraSensor>();
        lidarSensor = GetComponent<UnityLidarSensor>();

        // Get ROS socket from connection manager
        var connectionManager = FindObjectOfType<ROSConnectionManager>();
        rosSocket = connectionManager.GetComponent<ROSConnectionManager>().rosSocket;
    }

    public void PublishImage(Texture2D image)
    {
        Image rosImage = new Image();
        // Convert Unity texture to ROS Image message
        rosSocket.Publish(imageTopic, rosImage);
    }

    public void PublishLidar(float[] ranges, float[] intensities)
    {
        LaserScan laserScan = new LaserScan();
        laserScan.ranges = ranges;
        laserScan.intensities = intensities;
        laserScan.angle_min = Mathf.Deg2Rad * cameraSensor.minAngle;
        laserScan.angle_max = Mathf.Deg2Rad * cameraSensor.maxAngle;
        laserScan.angle_increment = (laserScan.angle_max - laserScan.angle_min) / ranges.Length;
        laserScan.range_min = 0.1f;
        laserScan.range_max = cameraSensor.maxRange;

        rosSocket.Publish(lidarTopic, laserScan);
    }
}
```

## Environment Design for Humanoid Robots

### Creating Realistic Environments
```csharp
// EnvironmentDesigner.cs - Create realistic environments
using UnityEngine;
using System.Collections.Generic;

public class EnvironmentDesigner : MonoBehaviour
{
    [Header("Environment Types")]
    public GameObject[] indoorScenes;
    public GameObject[] outdoorScenes;
    public GameObject[] obstaclePrefabs;

    [Header("Terrain Configuration")]
    public float terrainWidth = 100f;
    public float terrainLength = 100f;
    public AnimationCurve terrainHeightCurve;

    public void GenerateRandomEnvironment()
    {
        // Create terrain
        GameObject terrain = GameObject.CreatePrimitive(PrimitiveType.Plane);
        terrain.transform.localScale = new Vector3(terrainWidth / 10, 1, terrainLength / 10);

        // Add obstacles
        int obstacleCount = Random.Range(5, 15);
        for (int i = 0; i < obstacleCount; i++)
        {
            Vector3 position = new Vector3(
                Random.Range(-terrainWidth/2, terrainWidth/2),
                0,
                Random.Range(-terrainLength/2, terrainLength/2)
            );

            GameObject obstacle = Instantiate(
                obstaclePrefabs[Random.Range(0, obstaclePrefabs.Length)],
                position,
                Quaternion.identity
            );
        }
    }

    public void CreateUrbanEnvironment()
    {
        // Create city-like environment with buildings, roads, etc.
        // Implementation depends on specific requirements
    }

    public void CreateNaturalEnvironment()
    {
        // Create outdoor environment with trees, rocks, etc.
        // Implementation depends on specific requirements
    }
}
```

## Performance Optimization

### Optimizing for Real-time Simulation
```csharp
// PerformanceOptimizer.cs - Optimize Unity performance
using UnityEngine;

public class PerformanceOptimizer : MonoBehaviour
{
    [Header("Performance Settings")]
    public int targetFrameRate = 60;
    public LODGroup[] lodGroups;
    public bool enableOcclusionCulling = true;
    public bool enableDynamicBatching = true;
    public bool enableStaticBatching = true;

    void Start()
    {
        Application.targetFrameRate = targetFrameRate;
        QualitySettings.maxQueuedFrames = 2;

        SetupLODs();
        OptimizeRendering();
    }

    void SetupLODs()
    {
        foreach (LODGroup lodGroup in lodGroups)
        {
            lodGroup.animateCrossFading = true;
        }
    }

    void OptimizeRendering()
    {
        // These are set in Player Settings in Unity Editor
        // Dynamic Batching: Quality Settings
        // Static Batching: Edit -> Project Settings -> Player -> Other Settings
        // Occlusion Culling: Window -> Rendering -> Occlusion Culling
    }

    void Update()
    {
        // Monitor performance
        float frameTime = 1.0f / Time.smoothDeltaTime;
        if (frameTime < targetFrameRate * 0.8f)
        {
            // Consider reducing quality settings
            Debug.LogWarning($"Performance warning: {frameTime:F1} FPS");
        }
    }
}
```

## Practical Exercise

### Exercise 1: Unity Environment Setup
1. Create a new Unity project with robotics packages
2. Set up a basic environment with lighting and physics
3. Import or create a simple humanoid robot model
4. Configure coordinate system conversion between Unity and ROS

### Exercise 2: Sensor Integration
1. Implement camera sensor simulation in Unity
2. Create LiDAR simulation using raycasting
3. Set up ROS connection using ROS#
4. Publish sensor data to ROS topics

### Exercise 3: Environment Design
1. Create an indoor environment (rooms, corridors)
2. Add outdoor environment (terrain, obstacles)
3. Implement environment switching
4. Test with your humanoid robot model

## Advanced Topics

### Unity Perception Package
Unity Perception adds synthetic data generation capabilities:
- Domain randomization
- Synthetic dataset generation
- Sensor simulation with ground truth

### ML-Agents Integration
For training humanoid locomotion:
- Reinforcement learning environments
- Behavior training
- Curriculum learning

### Multi-camera Systems
```csharp
// StereoCameraSystem.cs - Implement stereo vision
using UnityEngine;

public class StereoCameraSystem : MonoBehaviour
{
    public Camera leftCamera;
    public Camera rightCamera;
    public float interaxialDistance = 0.064f; // Average human IPD

    void Start()
    {
        SetupStereoCameras();
    }

    void SetupStereoCameras()
    {
        if (leftCamera == null || rightCamera == null)
        {
            Debug.LogError("Left and right cameras must be assigned");
            return;
        }

        // Position cameras with interaxial distance
        Vector3 centerPos = transform.position;
        leftCamera.transform.position = centerPos + transform.right * (-interaxialDistance / 2);
        rightCamera.transform.position = centerPos + transform.right * (interaxialDistance / 2);

        // Ensure both cameras have same settings
        rightCamera.fieldOfView = leftCamera.fieldOfView;
        rightCamera.aspect = leftCamera.aspect;
    }
}
```

## Summary

This week covered high-fidelity rendering in Unity:
- Unity setup for robotics simulation
- Advanced rendering techniques (PBR, lighting, post-processing)
- Sensor simulation (camera, LiDAR, IMU)
- Unity-ROS integration
- Environment design for humanoid robots
- Performance optimization techniques

## Next Week Preview

Module 3 begins with Week 8: Isaac Sim for photorealistic simulation, where you'll learn to use NVIDIA's Isaac Sim platform for advanced robotics simulation with photorealistic rendering and AI integration.