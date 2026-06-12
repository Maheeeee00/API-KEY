#if UNITY_EDITOR
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.SceneManagement;

public static class BattleRoyaleMapBuilder
{
  private const string ScenePath = "Assets/Scenes/BattleRoyaleIsland.unity";
  private const string PrefabRoot = "Assets/Prefabs";
  private const string ArtRoot = "Assets/Art";

  [MenuItem("Battle Royale/Build Complete Free Fire Style Map")]
  public static void BuildCompleteMap()
  {
    EnsureFolders();
    Dictionary<string, GameObject> modelPrefabs = ImportModelPrefabs();
    CreateLootPrefabs(modelPrefabs);
    CreateCharacterPrefabs(modelPrefabs);

    Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
    SetupLighting();
    Terrain terrain = CreateIslandTerrain();
    GameObject systems = CreateGameSystems(terrain);
    GameObject environment = CreateEnvironment(modelPrefabs, terrain);
    GameObject player = CreatePlayer(modelPrefabs);
    CreateUI();
    CreatePlane();

    WireReferences(systems, environment, player, terrain);
    BakeNavMesh(terrain.gameObject);

    EditorSceneManager.SaveScene(scene, ScenePath);
    AssetDatabase.SaveAssets();
    AssetDatabase.Refresh();

    Debug.Log("Free Fire style map built! Open Assets/Scenes/BattleRoyaleIsland.unity and press Play.");
  }

  private static void EnsureFolders()
  {
    Directory.CreateDirectory("Assets/Scenes");
    Directory.CreateDirectory(PrefabRoot + "/Loot");
    Directory.CreateDirectory(PrefabRoot + "/Characters");
    Directory.CreateDirectory(PrefabRoot + "/Environment");
    Directory.CreateDirectory(PrefabRoot + "/Weapons");
  }

  private static Dictionary<string, GameObject> ImportModelPrefabs()
  {
    Dictionary<string, GameObject> map = new Dictionary<string, GameObject>();
    string[] fbxGuids = AssetDatabase.FindAssets("t:Model", new[] { ArtRoot });

    foreach (string guid in fbxGuids)
    {
      string path = AssetDatabase.GUIDToAssetPath(guid);
      if (!path.EndsWith(".fbx", System.StringComparison.OrdinalIgnoreCase))
      {
        continue;
      }

      string fileName = Path.GetFileName(path);
      GameObject source = AssetDatabase.LoadAssetAtPath<GameObject>(path);
      if (source == null)
      {
        continue;
      }

      string prefabPath = PrefabRoot + "/Environment/" + fileName.Replace(".fbx", ".prefab");
      GameObject prefab = PrefabUtility.SaveAsPrefabAsset(source, prefabPath);
      map[fileName] = prefab;
    }

    return map;
  }

  private static void CreateLootPrefabs(Dictionary<string, GameObject> models)
  {
    CreateWeaponLoot(WeaponId.AK47, models);
    CreateWeaponLoot(WeaponId.SCAR, models);
    CreateWeaponLoot(WeaponId.MP40, models);
    CreateWeaponLoot(WeaponId.M1014, models);
    CreateWeaponLoot(WeaponId.AWM, models);

    GameObject medkit = CreateLootBase("MedkitPickup", new Color(1f, 0.2f, 0.2f));
    medkit.AddComponent<MedkitPickup>();
    SavePrefab(medkit, PrefabRoot + "/Loot/MedkitPickup.prefab");

  CreateGearLoot("HelmetPickup_L1", GearType.Helmet, GearLevel.Level1, new Color(0.7f, 0.7f, 0.7f));
    CreateGearLoot("VestPickup_L2", GearType.Vest, GearLevel.Level2, new Color(0.2f, 0.5f, 1f));
    CreateGearLoot("BackpackPickup_L3", GearType.Backpack, GearLevel.Level3, new Color(0.9f, 0.7f, 0.2f));
  }

  private static void CreateWeaponLoot(WeaponId id, Dictionary<string, GameObject> models)
  {
    string modelFile = WeaponModelMapping.GetModelFileName(id);
    GameObject loot = CreateLootBase("WeaponPickup_" + id, new Color(0.9f, 0.85f, 0.2f));

    if (models.TryGetValue(modelFile, out GameObject weaponModel))
    {
      GameObject visual = (GameObject)PrefabUtility.InstantiatePrefab(weaponModel);
      visual.transform.SetParent(loot.transform, false);
      visual.transform.localPosition = Vector3.up * 0.4f;
      visual.transform.localRotation = Quaternion.Euler(0f, 90f, 0f);
      visual.transform.localScale = Vector3.one * 0.8f;
    }

    WeaponPickup pickup = loot.AddComponent<WeaponPickup>();
    SerializedObject so = new SerializedObject(pickup);
    so.FindProperty("weaponId").enumValueIndex = (int)id;
    so.ApplyModifiedPropertiesWithoutUndo();

    SavePrefab(loot, PrefabRoot + "/Loot/WeaponPickup_" + id + ".prefab");
  }

  private static void CreateGearLoot(string name, GearType type, GearLevel level, Color color)
  {
    GameObject loot = CreateLootBase(name, color);
    GearPickup pickup = loot.AddComponent<GearPickup>();
    SerializedObject so = new SerializedObject(pickup);
    so.FindProperty("gearType").enumValueIndex = (int)type;
    so.FindProperty("gearLevel").enumValueIndex = (int)level;
    so.ApplyModifiedPropertiesWithoutUndo();
    SavePrefab(loot, PrefabRoot + "/Loot/" + name + ".prefab");
  }

  private static GameObject CreateLootBase(string name, Color color)
  {
    GameObject loot = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
    loot.name = name;
    loot.transform.localScale = new Vector3(0.6f, 0.15f, 0.6f);
    Object.DestroyImmediate(loot.GetComponent<Collider>());
    SphereCollider trigger = loot.AddComponent<SphereCollider>();
    trigger.isTrigger = true;
    trigger.radius = 1.2f;
    loot.AddComponent<LootTag>();

    Renderer renderer = loot.GetComponent<Renderer>();
    Material mat = new Material(Shader.Find("Standard"));
    mat.color = color;
    renderer.sharedMaterial = mat;
    AssetDatabase.CreateAsset(mat, PrefabRoot + "/Loot/" + name + "_Mat.mat");

    return loot;
  }

  private static void CreateCharacterPrefabs(Dictionary<string, GameObject> models)
  {
    GameObject bot = CreateHumanoid("Bot", new Color(0.85f, 0.3f, 0.3f), false);
    bot.AddComponent<NavMeshAgent>();
    bot.AddComponent<EnemyAI>();
    bot.AddComponent<BotHealth>();
    bot.AddComponent<BotInventory>();
    bot.AddComponent<BotVision>();
    bot.AddComponent<ParachuteController>();
    bot.AddComponent<SafeZoneDamage>();
    bot.AddComponent<AICulling>();
    bot.AddComponent<NavMeshAgentWrapper>();

    GameObject weaponChild = new GameObject("Weapon");
    weaponChild.transform.SetParent(bot.transform);
    weaponChild.transform.localPosition = new Vector3(0.3f, 1.1f, 0.4f);
    weaponChild.AddComponent<WeaponController>();
    SavePrefab(bot, PrefabRoot + "/Characters/Bot.prefab");

    GameObject player = CreateHumanoid("Player", new Color(0.3f, 0.6f, 1f), true);
    player.tag = "Player";
    CharacterController cc = player.AddComponent<CharacterController>();
    cc.height = 1.8f;
    cc.radius = 0.35f;
    player.AddComponent<PlayerController>();
    player.AddComponent<PlayerHealth>();
    player.AddComponent<PlayerInventory>();
    player.AddComponent<ParachuteController>();
    player.AddComponent<SafeZoneDamage>();

    GameObject camPivot = new GameObject("CameraPivot");
    camPivot.transform.SetParent(player.transform);
    camPivot.transform.localPosition = new Vector3(0f, 1.6f, 0f);

    GameObject camObj = new GameObject("PlayerCamera");
    camObj.transform.SetParent(camPivot.transform);
    camObj.transform.localPosition = Vector3.zero;
    Camera cam = camObj.AddComponent<Camera>();
    cam.tag = "MainCamera";
    player.AddComponent<AudioListener>();

    GameObject playerWeapon = new GameObject("Weapon");
    playerWeapon.transform.SetParent(player.transform);
    playerWeapon.transform.localPosition = new Vector3(0.3f, 1.1f, 0.4f);
    playerWeapon.AddComponent<WeaponController>();

    SavePrefab(player, PrefabRoot + "/Characters/Player.prefab");
  }

  private static GameObject CreateHumanoid(string name, Color color, bool isPlayer)
  {
    GameObject root = new GameObject(name);
    GameObject body = GameObject.CreatePrimitive(PrimitiveType.Capsule);
    body.name = "Body";
    body.transform.SetParent(root.transform, false);
    body.transform.localPosition = new Vector3(0f, 1f, 0f);
    Object.DestroyImmediate(body.GetComponent<CapsuleCollider>());

    Material mat = new Material(Shader.Find("Standard"));
    mat.color = color;
    body.GetComponent<Renderer>().sharedMaterial = mat;
    AssetDatabase.CreateAsset(mat, PrefabRoot + "/Characters/" + name + "_Body.mat");

    if (!isPlayer)
    {
      CapsuleCollider col = root.AddComponent<CapsuleCollider>();
      col.height = 2f;
      col.radius = 0.4f;
      col.center = new Vector3(0f, 1f, 0f);
    }

    return root;
  }

  private static void SetupLighting()
  {
    RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Trilight;
    RenderSettings.ambientSkyColor = new Color(0.55f, 0.75f, 0.95f);
    RenderSettings.ambientEquatorColor = new Color(0.45f, 0.55f, 0.45f);
    RenderSettings.ambientGroundColor = new Color(0.25f, 0.3f, 0.2f);

    GameObject sun = new GameObject("Directional Light");
    Light light = sun.AddComponent<Light>();
    light.type = LightType.Directional;
    light.intensity = 1.2f;
    light.color = new Color(1f, 0.96f, 0.85f);
    sun.transform.rotation = Quaternion.Euler(50f, -30f, 0f);
  }

  private static Terrain CreateIslandTerrain()
  {
    TerrainData data = new TerrainData();
    data.heightmapResolution = 257;
    data.size = new Vector3(800f, 120f, 800f);

    float[,] heights = new float[data.heightmapResolution, data.heightmapResolution];
    int res = data.heightmapResolution;
    Vector2 center = new Vector2(res * 0.5f, res * 0.5f);
    float islandRadius = res * 0.42f;

    for (int y = 0; y < res; y++)
    {
      for (int x = 0; x < res; x++)
      {
        float dist = Vector2.Distance(new Vector2(x, y), center);
        float island = Mathf.Clamp01(1f - dist / islandRadius);
        island = Mathf.Pow(island, 1.4f);
        float noise = Mathf.PerlinNoise(x * 0.04f, y * 0.04f) * 0.12f;
        float hills = Mathf.PerlinNoise(x * 0.015f + 50f, y * 0.015f + 50f) * 0.08f;
        heights[y, x] = Mathf.Clamp01(island * 0.55f + noise * island + hills * island);
      }
    }

    data.SetHeights(0, 0, heights);

    GameObject terrainObject = Terrain.CreateTerrainGameObject(data);
    terrainObject.name = "IslandTerrain";
    terrainObject.transform.position = new Vector3(-400f, 0f, -400f);

    TerrainLayer sand = new TerrainLayer();
    sand.diffuseTexture = CreateSolidTexture(new Color(0.86f, 0.78f, 0.55f), "Sand");
    TerrainLayer grass = new TerrainLayer();
    grass.diffuseTexture = CreateSolidTexture(new Color(0.28f, 0.62f, 0.28f), "Grass");
    data.terrainLayers = new[] { sand, grass };

    AssetDatabase.CreateAsset(data, "Assets/Scenes/IslandTerrainData.asset");
    AssetDatabase.CreateAsset(sand, "Assets/Scenes/TerrainLayer_Sand.terrainlayer");
    AssetDatabase.CreateAsset(grass, "Assets/Scenes/TerrainLayer_Grass.terrainlayer");

    return terrainObject.GetComponent<Terrain>();
  }

  private static Texture2D CreateSolidTexture(Color color, string name)
  {
    Texture2D tex = new Texture2D(4, 4);
    Color[] pixels = new Color[16];
    for (int i = 0; i < pixels.Length; i++) pixels[i] = color;
    tex.SetPixels(pixels);
    tex.Apply();
    AssetDatabase.CreateAsset(tex, "Assets/Scenes/TerrainTex_" + name + ".asset");
    return tex;
  }

  private static GameObject CreateGameSystems(Terrain terrain)
  {
    GameObject root = new GameObject("GameSystems");

    GameObject zoneCircle = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
    zoneCircle.name = "SafeZoneCircle";
    zoneCircle.transform.SetParent(root.transform);
    zoneCircle.transform.position = new Vector3(0f, 2f, 0f);
    zoneCircle.transform.localScale = new Vector3(800f, 0.1f, 800f);
    Object.DestroyImmediate(zoneCircle.GetComponent<Collider>());
    Material zoneMat = new Material(Shader.Find("Standard"));
    zoneMat.color = new Color(0.2f, 0.8f, 1f, 0.25f);
    zoneMat.SetFloat("_Mode", 3);
    zoneMat.SetInt("_SrcBlend", (int)UnityEngine.Rendering.BlendMode.SrcAlpha);
    zoneMat.SetInt("_DstBlend", (int)UnityEngine.Rendering.BlendMode.OneMinusSrcAlpha);
    zoneMat.SetInt("_ZWrite", 0);
    zoneMat.DisableKeyword("_ALPHATEST_ON");
    zoneMat.EnableKeyword("_ALPHABLEND_ON");
    zoneMat.renderQueue = 3000;
    zoneCircle.GetComponent<Renderer>().sharedMaterial = zoneMat;
    AssetDatabase.CreateAsset(zoneMat, "Assets/Scenes/SafeZoneMat.mat");

    root.AddComponent<ZoneManager>();
    root.AddComponent<GameManager>();
    root.AddComponent<ItemSpawner>();
    root.AddComponent<BotSpawnManager>();

    return root;
  }

  private static GameObject CreateEnvironment(Dictionary<string, GameObject> models, Terrain terrain)
  {
    GameObject root = new GameObject("Environment");
    MapEnvironmentSpawner spawner = root.AddComponent<MapEnvironmentSpawner>();

    List<GameObject> buildings = new List<GameObject>();
    List<GameObject> trees = new List<GameObject>();
    List<GameObject> props = new List<GameObject>();

    foreach (KeyValuePair<string, GameObject> entry in models)
    {
      string name = entry.Key.ToLowerInvariant();
      if (name.Contains("building") || name.Contains("module") || name.Contains("structure"))
      {
        buildings.Add(entry.Value);
      }
      else if (name.Contains("tree") || name.Contains("palm") || name.Contains("grass-large"))
      {
        trees.Add(entry.Value);
      }
      else if (name.Contains("rock") || name.Contains("barrel") || name.Contains("crate") || name.Contains("box") || name.Contains("fence"))
      {
        props.Add(entry.Value);
      }
    }

    if (buildings.Count == 0)
    {
      buildings.Add(CreateFallbackBuilding());
    }

    if (trees.Count == 0)
    {
      trees.Add(CreateFallbackTree());
    }

    if (props.Count == 0)
    {
      props.Add(CreateFallbackCrate());
    }

    SerializedObject so = new SerializedObject(spawner);
    SetPrefabList(so, "buildingPrefabs", buildings);
    SetPrefabList(so, "treePrefabs", trees);
    SetPrefabList(so, "propPrefabs", props);
    so.ApplyModifiedPropertiesWithoutUndo();

    spawner.SpawnEnvironment();
    return root;
  }

  private static GameObject CreateFallbackBuilding()
  {
    GameObject cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
    cube.name = "FallbackBuilding";
    cube.transform.localScale = new Vector3(6f, 8f, 6f);
    return SavePrefab(cube, PrefabRoot + "/Environment/FallbackBuilding.prefab");
  }

  private static GameObject CreateFallbackTree()
  {
    GameObject tree = new GameObject("FallbackTree");
    GameObject trunk = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
    trunk.transform.SetParent(tree.transform, false);
    trunk.transform.localScale = new Vector3(0.4f, 2f, 0.4f);
    trunk.transform.localPosition = new Vector3(0f, 1f, 0f);
    GameObject leaves = GameObject.CreatePrimitive(PrimitiveType.Sphere);
    leaves.transform.SetParent(tree.transform, false);
    leaves.transform.localPosition = new Vector3(0f, 3f, 0f);
    leaves.transform.localScale = Vector3.one * 2f;
    return SavePrefab(tree, PrefabRoot + "/Environment/FallbackTree.prefab");
  }

  private static GameObject CreateFallbackCrate()
  {
    GameObject crate = GameObject.CreatePrimitive(PrimitiveType.Cube);
    crate.name = "FallbackCrate";
    crate.transform.localScale = new Vector3(1.5f, 1.5f, 1.5f);
    return SavePrefab(crate, PrefabRoot + "/Environment/FallbackCrate.prefab");
  }

  private static GameObject CreatePlayer(Dictionary<string, GameObject> models)
  {
    GameObject playerPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabRoot + "/Characters/Player.prefab");
    GameObject player = (GameObject)PrefabUtility.InstantiatePrefab(playerPrefab);
    player.name = "Player";
    player.transform.position = new Vector3(0f, 150f, 0f);
    return player;
  }

  private static void CreateUI()
  {
    GameObject canvasObj = new GameObject("UI");
    Canvas canvas = canvasObj.AddComponent<Canvas>();
    canvas.renderMode = RenderMode.ScreenSpaceOverlay;
    canvasObj.AddComponent<UnityEngine.UI.CanvasScaler>();
    canvasObj.AddComponent<UnityEngine.UI.GraphicRaycaster>();

    GameObject eventSystem = new GameObject("EventSystem");
    eventSystem.AddComponent<UnityEngine.EventSystems.EventSystem>();
    eventSystem.AddComponent<UnityEngine.EventSystems.StandaloneInputModule>();

    canvasObj.AddComponent<HUDController>();
    canvasObj.AddComponent<MobileInput>();
    canvasObj.AddComponent<MinimapController>();

    CreateHudText(canvasObj.transform, "AliveText", "Alive: 50", new Vector2(-20f, -20f), new Vector2(1f, 1f), new Vector2(1f, 1f));
    CreateHudText(canvasObj.transform, "WeaponText", "Unarmed", new Vector2(20f, 20f), new Vector2(0f, 0f), new Vector2(0f, 0f));
  }

  private static void CreateHudText(Transform parent, string name, string text, Vector2 anchoredPos, Vector2 anchorMin, Vector2 anchorMax)
  {
    GameObject obj = new GameObject(name);
    obj.transform.SetParent(parent, false);
    RectTransform rect = obj.AddComponent<RectTransform>();
    rect.anchorMin = anchorMin;
    rect.anchorMax = anchorMax;
    rect.pivot = anchorMin;
    rect.anchoredPosition = anchoredPos;
    rect.sizeDelta = new Vector2(260f, 40f);
    UnityEngine.UI.Text label = obj.AddComponent<UnityEngine.UI.Text>();
    label.text = text;
    label.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
    label.fontSize = 22;
    label.color = Color.white;
  }

  private static void CreatePlane()
  {
    GameObject planeRoot = new GameObject("PlaneSystem");
    PlaneController controller = planeRoot.AddComponent<PlaneController>();

    GameObject planeModel = GameObject.CreatePrimitive(PrimitiveType.Cube);
    planeModel.name = "PlaneModel";
    planeModel.transform.SetParent(planeRoot.transform);
    planeModel.transform.localScale = new Vector3(8f, 1f, 20f);
    planeModel.transform.localPosition = new Vector3(0f, 150f, 0f);
    Object.DestroyImmediate(planeModel.GetComponent<BoxCollider>());

    SerializedObject so = new SerializedObject(controller);
    so.FindProperty("planeModel").objectReferenceValue = planeModel.transform;
    so.ApplyModifiedPropertiesWithoutUndo();
  }

  private static void WireReferences(GameObject systems, GameObject environment, GameObject player, Terrain terrain)
  {
    ZoneManager zone = systems.GetComponent<ZoneManager>();
    GameManager game = systems.GetComponent<GameManager>();
    ItemSpawner items = systems.GetComponent<ItemSpawner>();
    BotSpawnManager bots = systems.GetComponent<BotSpawnManager>();

    Transform zoneCircle = systems.transform.Find("SafeZoneCircle");

    SerializedObject zoneSo = new SerializedObject(zone);
    zoneSo.FindProperty("safeZoneCircle").objectReferenceValue = zoneCircle;
    zoneSo.ApplyModifiedPropertiesWithoutUndo();

    GameObject botPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabRoot + "/Characters/Bot.prefab");
    List<GameObject> lootPrefabs = new List<GameObject>();
    string[] lootGuids = AssetDatabase.FindAssets("t:Prefab", new[] { PrefabRoot + "/Loot" });
    foreach (string guid in lootGuids)
    {
      lootPrefabs.Add(AssetDatabase.LoadAssetAtPath<GameObject>(AssetDatabase.GUIDToAssetPath(guid)));
    }

    SerializedObject gameSo = new SerializedObject(game);
    gameSo.FindProperty("player").objectReferenceValue = player.GetComponent<PlayerController>();
    gameSo.FindProperty("botSpawnManager").objectReferenceValue = bots;
    gameSo.FindProperty("itemSpawner").objectReferenceValue = items;
    gameSo.FindProperty("planeController").objectReferenceValue = Object.FindFirstObjectByType<PlaneController>();
    gameSo.ApplyModifiedPropertiesWithoutUndo();

    SerializedObject itemSo = new SerializedObject(items);
    SerializedProperty list = itemSo.FindProperty("lootPrefabs");
    list.ClearArray();
    for (int i = 0; i < lootPrefabs.Count; i++)
    {
      list.InsertArrayElementAtIndex(i);
      list.GetArrayElementAtIndex(i).FindPropertyRelative("prefab").objectReferenceValue = lootPrefabs[i];
      list.GetArrayElementAtIndex(i).FindPropertyRelative("weight").floatValue = 1f;
    }
    itemSo.ApplyModifiedPropertiesWithoutUndo();

    SerializedObject botSo = new SerializedObject(bots);
    botSo.FindProperty("botPrefab").objectReferenceValue = botPrefab;
    botSo.ApplyModifiedPropertiesWithoutUndo();

    terrain.gameObject.isStatic = true;
    GameObjectUtility.SetStaticEditorFlags(terrain.gameObject, StaticEditorFlags.NavigationStatic);
  }

  private static void BakeNavMesh(Terrain terrain)
  {
    GameObjectUtility.SetStaticEditorFlags(terrain.gameObject, StaticEditorFlags.NavigationStatic);
    UnityEditor.AI.NavMeshBuilder.BuildNavMesh();
  }

  private static void SetPrefabList(SerializedObject so, string propertyName, List<GameObject> prefabs)
  {
    SerializedProperty list = so.FindProperty(propertyName);
    list.ClearArray();
    for (int i = 0; i < prefabs.Count; i++)
    {
      list.InsertArrayElementAtIndex(i);
      list.GetArrayElementAtIndex(i).objectReferenceValue = prefabs[i];
    }
  }

  private static GameObject SavePrefab(GameObject obj, string path)
  {
    GameObject prefab = PrefabUtility.SaveAsPrefabAsset(obj, path);
    Object.DestroyImmediate(obj);
    return prefab;
  }
}
#endif
