using System.Collections.Generic;
using UnityEngine;

public class ItemSpawner : MonoBehaviour
{
  [System.Serializable]
  public class LootPrefabEntry
  {
    public GameObject prefab;
    [Range(0f, 1f)] public float weight = 1f;
  }

  [SerializeField] private int lootCount = 100;
  [SerializeField] private Vector2 mapBounds = new Vector2(350f, 350f);
  [SerializeField] private float spawnHeight = 1f;
  [SerializeField] private LayerMask groundMask = ~0;
  [SerializeField] private List<LootPrefabEntry> lootPrefabs = new List<LootPrefabEntry>();
  [SerializeField] private Transform lootParent;

  private readonly List<GameObject> spawnedLoot = new List<GameObject>();

  public IReadOnlyList<GameObject> SpawnedLoot => spawnedLoot;

  public void SpawnLoot()
  {
    ClearLoot();

    for (int i = 0; i < lootCount; i++)
    {
      Vector3 position = GetRandomGroundPosition();
      GameObject prefab = PickRandomPrefab();
      if (prefab == null)
      {
        continue;
      }

      GameObject instance = Instantiate(prefab, position, Quaternion.identity, lootParent);
      spawnedLoot.Add(instance);
    }
  }

  public void ClearLoot()
  {
    foreach (GameObject loot in spawnedLoot)
    {
      if (loot != null)
      {
        Destroy(loot);
      }
    }

    spawnedLoot.Clear();
  }

  private Vector3 GetRandomGroundPosition()
  {
    for (int attempt = 0; attempt < 8; attempt++)
    {
      float x = Random.Range(-mapBounds.x, mapBounds.x);
      float z = Random.Range(-mapBounds.y, mapBounds.y);
      Vector3 origin = new Vector3(x, 500f, z);

      if (Physics.Raycast(origin, Vector3.down, out RaycastHit hit, 1000f, groundMask, QueryTriggerInteraction.Ignore))
      {
        return hit.point + Vector3.up * spawnHeight;
      }
    }

    return new Vector3(Random.Range(-mapBounds.x, mapBounds.x), spawnHeight, Random.Range(-mapBounds.y, mapBounds.y));
  }

  private GameObject PickRandomPrefab()
  {
    if (lootPrefabs.Count == 0)
    {
      return null;
    }

    float totalWeight = 0f;
    foreach (LootPrefabEntry entry in lootPrefabs)
    {
      totalWeight += entry.weight;
    }

    float roll = Random.Range(0f, totalWeight);
    float cumulative = 0f;

    foreach (LootPrefabEntry entry in lootPrefabs)
    {
      cumulative += entry.weight;
      if (roll <= cumulative)
      {
        return entry.prefab;
      }
    }

    return lootPrefabs[0].prefab;
  }
}
