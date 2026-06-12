using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Populates the island with buildings, trees, and containers at runtime or from the Editor builder.
/// Assign generated prefab lists from Battle Royale > Build Complete Map.
/// </summary>
public class MapEnvironmentSpawner : MonoBehaviour
{
  [SerializeField] private List<GameObject> buildingPrefabs = new List<GameObject>();
  [SerializeField] private List<GameObject> treePrefabs = new List<GameObject>();
  [SerializeField] private List<GameObject> propPrefabs = new List<GameObject>();
  [SerializeField] private int buildingCount = 45;
  [SerializeField] private int treeCount = 120;
  [SerializeField] private int propCount = 60;
  [SerializeField] private float mapRadius = 320f;
  [SerializeField] private Transform environmentRoot;

  public void SpawnEnvironment()
  {
    if (environmentRoot == null)
    {
      environmentRoot = transform;
    }

    ClearChildren(environmentRoot);
    PlaceRandom(buildingPrefabs, buildingCount, 8f, 35f);
    PlaceRandom(treePrefabs, treeCount, 2f, 8f);
    PlaceRandom(propPrefabs, propCount, 1f, 4f);
  }

  private void PlaceRandom(List<GameObject> prefabs, int count, float minScale, float maxScale)
  {
    if (prefabs == null || prefabs.Count == 0)
    {
      return;
    }

    for (int i = 0; i < count; i++)
    {
      Vector3 position = GetRandomGroundPoint();
      GameObject prefab = prefabs[Random.Range(0, prefabs.Count)];
      GameObject instance = Instantiate(prefab, position, Quaternion.Euler(0f, Random.Range(0f, 360f), 0f), environmentRoot);
      float scale = Random.Range(minScale, maxScale);
      instance.transform.localScale = Vector3.one * scale;
    }
  }

  private Vector3 GetRandomGroundPoint()
  {
    for (int attempt = 0; attempt < 12; attempt++)
    {
      Vector2 circle = Random.insideUnitCircle * mapRadius;
      Vector3 origin = new Vector3(circle.x, 300f, circle.y);
      if (Physics.Raycast(origin, Vector3.down, out RaycastHit hit, 600f))
      {
        return hit.point;
      }
    }

    return new Vector3(Random.Range(-mapRadius, mapRadius), 0f, Random.Range(-mapRadius, mapRadius));
  }

  private void ClearChildren(Transform root)
  {
    for (int i = root.childCount - 1; i >= 0; i--)
    {
      GameObject child = root.GetChild(i).gameObject;
      if (Application.isPlaying)
      {
        Destroy(child);
      }
      else
      {
        DestroyImmediate(child);
      }
    }
  }
}
